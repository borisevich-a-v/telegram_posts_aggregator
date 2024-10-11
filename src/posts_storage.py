from datetime import datetime

from loguru import logger
from sqlalchemy import func
from sqlalchemy.orm import Session
from telethon.tl.types import Message
from telethon.utils import get_peer_id

from models import ChannelModel, ChannelType, MessageModel

MESSAGE_ID = int


class NoNewPosts(Exception):
    """Post storage raise this exception when there are no new posts"""


class PostDuplication(Exception):
    """This post has been saved into database previously, probably it's a repost or second time processing"""


class PostStorage:
    def __init__(self, session_maker) -> None:
        logger.info("Post storage is initializing...")
        self.session_maker = session_maker

    def post(self, message: Message) -> None:
        original_message_id = message.fwd_from.channel_post
        original_peer_id = get_peer_id(message.fwd_from.from_id)
        logger.info("Adding message {} from the {}...", original_message_id, original_peer_id)
        with self.session_maker() as session:
            orm_message = MessageModel(
                message_id=message.id,
                grouped_id=message.grouped_id,
                channel=self.get_or_create_channel(original_peer_id, session),
                original_message_id=original_message_id,
            )
            session.add(orm_message)
            session.commit()

    def get_or_create_channel(self, channel_id: int, session: Session) -> ChannelModel:
        channel = session.query(ChannelModel).filter_by(id=channel_id).first()
        if not channel:
            logger.info(f"Adding the new channel...: {channel}")
            channel = ChannelModel(id=channel_id)
            session.add(channel)
            session.commit()
        return channel

    def _get_first_unsent_message(self, session: Session, channel_type: ChannelType) -> MessageModel:
        unsent_message_query = session.query(MessageModel).join(ChannelModel).filter(MessageModel.sent.is_(None))
        if channel_type is not None:
            unsent_message_query = unsent_message_query.filter(ChannelModel.type == channel_type)

        first_unsent_message = unsent_message_query.order_by(MessageModel.id).first()

        if not first_unsent_message:
            raise NoNewPosts("No new posts in the storage")
        return first_unsent_message

    def get_oldest_unsent_post(self, channel_type: ChannelType = None) -> list[MESSAGE_ID]:
        # todo: optimize query
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

    def is_original_msg_duplicate(self, msgs: list[Message]) -> bool:
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
