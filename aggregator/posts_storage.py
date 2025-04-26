from datetime import datetime

from loguru import logger
from sqlalchemy.orm import joinedload, selectinload
from sqlalchemy import select, update

from sqlalchemy.ext.asyncio import AsyncSession
from telethon.tl.types import Message
from telethon.utils import get_peer_id

from aggregator.db import DatabaseSessionManager
from aggregator.models import (
    NOT_SPECIFIED_CHANNEL_TYPE,
    ChannelModel,
    ChannelTypeModel,
    MessageModel,
    MessageVectorModel,
)

MESSAGE_ID = int


class NoNewPosts(Exception):
    """Post storage raise this exception when there are no new posts"""


class PostDuplication(Exception):
    """This post has been saved into database previously, probably it's a repost or second time processing"""


class PostStorage:
    def __init__(self, sessionmanager: DatabaseSessionManager) -> None:
        logger.info("Post storage is initializing...")
        self.sessionmanager = sessionmanager

    async def post(
        self,
        tg_message_id: MESSAGE_ID,
        grouped_id: int,
        event_peer_id,
        original_channel_id,
        original_message_id,
        embedding: list[float] | None,
    ) -> None:
        async with self.sessionmanager.session() as session:
            message_orm = MessageModel(
                tg_message_id=tg_message_id,
                grouped_id=grouped_id,
                channel_id=event_peer_id,
                original_channel_id=original_channel_id,
                original_message_id=original_message_id,
            )
            session.add(message_orm)

            if embedding:
                embedding_orm = MessageVectorModel(message=message_orm, embedding=embedding)
                session.add(embedding_orm)

            await session.commit()

    async def get_first_unsent_message(self, channel_type: str | None, session: AsyncSession) -> MessageModel:
        stmt = (
            select(MessageModel)
            .options(selectinload(MessageModel.embedding))
            .join(ChannelModel)
            .where(MessageModel.sent.is_(None))
        )
        if channel_type:
            stmt = stmt.where(MessageModel.channel.type_ == channel_type)

        first = (await session.execute(stmt.order_by(MessageModel.id).limit(1))).scalar_one_or_none()

        if not first:
            raise NoNewPosts("No new posts in the storage")

        return first

    async def get_album_by_grouped_id(self, grouped_id: int, session: AsyncSession) -> list[MessageModel]:
        stmt = (
            select(MessageModel)
            .options(selectinload(MessageModel.embedding))
            .where(MessageModel.grouped_id == grouped_id)
        )
        res = await session.execute(stmt)
        return list(res.scalars().all())

    async def get_similar_posts(
        self,
        target_vec: list[float],
        session: AsyncSession,
        similarity_threshold: float = 0.6,
    ) -> list[list[MessageModel]]:
        logger.debug("Looking for similar posts")
        stmt = (
            select(MessageModel)
            .select_from(MessageVectorModel)
            .join(MessageModel, MessageModel.id == MessageVectorModel.message_id)
            .where(MessageVectorModel.embedding.cosine_distance(target_vec) < similarity_threshold)
            .order_by(MessageVectorModel.embedding.cosine_distance(target_vec), MessageModel.grouped_id)
        )

        msgs: list[MessageModel] = (await session.execute(stmt)).scalars().all()

        posts = []
        last_group_id = None
        for msg in msgs:
            if msg.grouped_id is None:
                posts.append([msg])
            elif msg.grouped_id != last_group_id:
                posts.append([msg])
            else:  # msg.grouped_id == last_group_id
                posts[-1].append(msg)

        return posts

    async def get_similar_messages_ids(self, embedding: list[float]) -> list[list[MESSAGE_ID]]:
        async with self.sessionmanager.session() as session:
            similar_posts = await self.get_similar_posts(embedding, session)
            return [[msg.tg_message_id for msg in post] for post in similar_posts]

    async def get_oldest_unsent_post(self, channel_type: str | None = None) -> list[MESSAGE_ID]:
        async with self.sessionmanager.session() as session:
            first_unsent_msg = await self.get_first_unsent_message(channel_type, session)
            if first_unsent_msg.grouped_id is None:
                msgs = [first_unsent_msg]
            else:
                msgs = await self.get_album_by_grouped_id(first_unsent_msg.grouped_id, session)
            return [msg.tg_message_id for msg in msgs]

    async def set_sent_multiple(self, message_ids: list[MESSAGE_ID]) -> None:
        async with self.sessionmanager.session() as session:
            stmt = update(MessageModel).where(MessageModel.tg_message_id.in_(message_ids)).values(sent=datetime.now())
            await session.execute(stmt)
            await session.commit()

    async def is_duplicate(self, msgs: list[Message]) -> bool:
        async with self.sessionmanager.session() as session:
            for msg in msgs:
                # If message is forwarded, then there is an obvious risk of duplication, if it is an original message
                # then there is still possibility that Telethon could catch this message multiple times, so we have to
                # doublecheck anyway
                if msg.fwd_from is None:
                    message_id = msg.id
                    channel_id = get_peer_id(msg.peer_id)
                else:
                    message_id = msg.fwd_from.channel_post
                    channel_id = get_peer_id(msg.fwd_from.from_id)
                stmt = select(MessageModel.id).where(
                    MessageModel.original_message_id == message_id, MessageModel.channel_id == channel_id
                )
                result = await session.execute(stmt)
                existing = result.scalar_one_or_none()
                if existing:
                    return True
        return False

    async def is_group_processed(self, grouped_id: int) -> bool:
        async with self.sessionmanager.session() as session:
            stmt = select(
                (
                    select(MessageModel.id)
                    .join(MessageVectorModel, MessageVectorModel.message_id == MessageModel.id)
                    .where(MessageModel.grouped_id == grouped_id, MessageVectorModel.id.isnot(None))
                ).exists()
            )

            result = await session.execute(stmt)
            is_processed = result.scalar_one_or_none()
            return bool(is_processed)

    async def get_all_custom_channel_types(self) -> list[str]:
        """Return all channels types except default one"""
        async with self.sessionmanager.session() as session:
            stmt = select(ChannelTypeModel.type_).where(ChannelTypeModel.type_ != NOT_SPECIFIED_CHANNEL_TYPE).distinct()
            types = await session.execute(stmt)
        return types.scalars().all()

    async def get_whitelisted_channel_ids(self) -> list[int]:
        async with self.sessionmanager.session() as session:
            channel_ids = await session.execute(select(ChannelModel.id))
            return channel_ids.scalars().all()

    async def add_channel(self, id_: int, name: str | None) -> None:
        async with self.sessionmanager.session() as session:
            session.add(ChannelModel(id=id_, name=name))
            await session.commit()

    async def get_all_channels(self) -> list[ChannelModel]:
        async with self.sessionmanager.session() as session:
            result = await session.execute(select(ChannelModel).options(joinedload(ChannelModel.type_)))
            return result.scalars().all()
