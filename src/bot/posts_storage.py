from datetime import datetime

from loguru import logger
from sqlalchemy import func
from telethon.tl.types import Message

from models import ChannelModel, MessageModel

MESSAGE_ID = int


class NoNewPosts(Exception):
    """Post storage raise this exception when there are no new posts"""


class PostStorage:
    def __init__(self, session_maker) -> None:
        logger.info("Post storage is initializing...")
        self.session_maker = session_maker

    def post(self, message: Message) -> None:
        with self.session_maker() as session:
            channel = self.get_or_create_channel(message.fwd_from.from_id.channel_id, session)
            message = MessageModel(message_id=message.id, grouped_id=message.grouped_id, channel=channel)
            session.add(message)
            session.commit()

    def get_or_create_channel(self, channel_id: int, session) -> ChannelModel:
        channel = session.query(ChannelModel).filter_by(channel_id=channel_id).first()
        if not channel:
            logger.info(f"Adding new channel...: {channel}")
            channel = ChannelModel(channel_id=channel_id)
            session.add(channel)
            session.commit()
        return channel

    def get_oldest_unsent_post(self) -> list[MESSAGE_ID]:
        # todo: should we use transactions here??
        with self.session_maker() as session:
            first_unsent_id = (
                session.query(func.min(MessageModel.id)).filter(MessageModel.sent.is_(None)).scalar_subquery()
            )
            first_unsent_message = session.query(MessageModel).filter(MessageModel.id == first_unsent_id).first()
            if not first_unsent_message:
                raise NoNewPosts("No new posts in the storage")
            if first_unsent_message.grouped_id is not None:
                messages = (
                    session.query(MessageModel.message_id)
                    .filter(MessageModel.grouped_id == first_unsent_message.grouped_id)
                    .all()
                )
                return [msg.message_id for msg in messages]
            else:
                return [first_unsent_message.message_id]

    def set_sent_multiple(self, message_ids: list[int]) -> None:
        with self.session_maker() as session:
            session.query(MessageModel).filter(MessageModel.message_id.in_(message_ids)).update(
                {MessageModel.sent: datetime.now()}
            )
            session.commit()
