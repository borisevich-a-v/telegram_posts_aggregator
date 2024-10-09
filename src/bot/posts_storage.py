from datetime import datetime

from loguru import logger
from sqlalchemy import func
from sqlalchemy.orm import Session
from telethon.tl.types import Message

from models import ChannelModel, MessageModel
from utils import get_entity_id

MSG_ID = int


class NoNewPosts(Exception):
    """Post storage raise this exception when there are no new posts"""


class PostDuplication(Exception):
    """This post has been saved into database previously, probably it's a repost or second time processing"""


class PostStorage:
    def __init__(self, session_maker) -> None:
        logger.info("Post storage is initializing...")
        self.session_maker = session_maker

    def post(self, msg: Message) -> None:
        with self.session_maker() as session:
            original_message_id = msg.fwd_from.channel_post
            original_peer_id = get_entity_id(msg.fwd_from.from_id)

            msg = MessageModel(
                message_id=msg.id,
                grouped_id=msg.grouped_id,
                channel=self.get_or_create_channel(original_peer_id, session),
                original_message_id=original_message_id,
            )
            session.add(msg)
            session.commit()

    def get_or_create_channel(self, channel_id: int, session: Session) -> ChannelModel:
        channel = session.query(ChannelModel).filter_by(channel_id=channel_id).first()
        if not channel:
            logger.info(f"Adding the new channel...: {channel}")
            channel = ChannelModel(channel_id=channel_id)
            session.add(channel)
            session.commit()
        return channel

    def get_oldest_unsent_post(self) -> list[MSG_ID]:
        # todo: write 1 query instead of 2
        with self.session_maker() as session:
            first_unsent_id = (
                session.query(func.min(MessageModel.id)).filter(MessageModel.sent.is_(None)).scalar_subquery()
            )
            first_unsent_msg = session.query(MessageModel).filter(MessageModel.id == first_unsent_id).first()
            if not first_unsent_msg:
                raise NoNewPosts("No new posts in the storage")
            if first_unsent_msg.grouped_id is not None:
                msgs = (
                    session.query(MessageModel.message_id)
                    .filter(MessageModel.grouped_id == first_unsent_msg.grouped_id)
                    .all()
                )
                return [msg.message_id for msg in msgs]
            else:
                return [first_unsent_msg.message_id]

    def set_sent_multiple(self, msg_ids: list[MSG_ID]) -> None:
        with self.session_maker() as session:
            session.query(MessageModel).filter(MessageModel.message_id.in_(msg_ids)).update(
                {MessageModel.sent: datetime.now()}
            )
            session.commit()

    def is_original_msg_duplicate(self, msgs: list[Message]) -> bool:
        with self.session_maker() as session:
            for msg in msgs:
                if bool(
                    session.query(MessageModel)
                    .filter(
                        MessageModel.original_message_id == msg.id,
                        MessageModel.channel_id == get_entity_id(msg.from_id),
                    )
                    .first()
                ):
                    return True
        return False
