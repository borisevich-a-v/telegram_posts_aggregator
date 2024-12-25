from datetime import datetime
from typing import Any

from loguru import logger
from sqlalchemy.orm import Session
from telethon.tl.types import Message
from telethon.utils import get_peer_id

from aggregator.models import NOT_SPECIFIED_CHANNEL_TYPE, ChannelModel, ChannelTypeModel, MessageModel

MESSAGE_ID = int


class NoNewPosts(Exception):
    """Post storage raise this exception when there are no new posts"""


class PostDuplication(Exception):
    """This post has been saved into database previously, probably it's a repost or second time processing"""


class PostStorage:
    def __init__(self, session_maker) -> None:
        logger.info("Post storage is initializing...")
        self.session_maker = session_maker

    def post(self, message_id: MESSAGE_ID, grouped_id: int , event_peer_id, original_channel_id, original_message_id) -> None:
        with self.session_maker() as session:
            orm_message = MessageModel(
                message_id=message_id,
                grouped_id=grouped_id,
                channel_id=event_peer_id,
                original_channel_id=original_channel_id,
                original_message_id=original_message_id,
            )
            session.add(orm_message)
            session.commit()

    def _get_first_unsent_message(self, session: Session, channel_type: Any) -> MessageModel:
        # My first code with SQLAlchemy, it's bad, but I'll fix it later
        unsent_message_query = session.query(MessageModel).join(ChannelModel).filter(MessageModel.sent.is_(None))
        if channel_type is not None:
            unsent_message_query = unsent_message_query.join(ChannelTypeModel).filter(
                ChannelTypeModel.type_ == channel_type
            )

        first_unsent_message = unsent_message_query.order_by(MessageModel.id).first()

        if not first_unsent_message:
            raise NoNewPosts("No new posts in the storage")
        return first_unsent_message

    def get_oldest_unsent_post(self, channel_type: str | None = None) -> list[MESSAGE_ID]:
        logger.debug("Channel type is {}", channel_type)
        with self.session_maker() as session:
            first_unsent_message = self._get_first_unsent_message(session, channel_type)

            if first_unsent_message.grouped_id is None:
                return [first_unsent_message.message_id]

            return [
                msg.message_id
                for msg in (
                    session.query(MessageModel.message_id)
                    .filter(MessageModel.grouped_id == first_unsent_message.grouped_id)
                    .all()
                )
            ]

    def set_sent_multiple(self, message_ids: list[MESSAGE_ID]) -> None:
        with self.session_maker() as session:
            session.query(MessageModel).filter(MessageModel.message_id.in_(message_ids)).update(
                {MessageModel.sent: datetime.now()}
            )
            session.commit()

    def is_duplicate(self, msgs: list[Message]) -> bool:
        with self.session_maker() as session:
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

                res = (
                    session.query(MessageModel)
                    .filter(MessageModel.original_message_id == message_id, MessageModel.channel_id == channel_id)
                    .first()
                )
                if res:
                    return True
        return False

    def get_all_custom_channel_types(self):
        """Return all channels types except default one"""
        with self.session_maker() as session:
            types = (
                session.query(ChannelTypeModel.type_).filter(ChannelTypeModel.type_ != NOT_SPECIFIED_CHANNEL_TYPE).all()
            )
        return [t[0] for t in types]

    def get_whitelisted_channel_ids(self) -> list[int]:
        with self.session_maker() as session:
            channel_ids = session.query(ChannelModel.id).all()
        return [t[0] for t in channel_ids]
