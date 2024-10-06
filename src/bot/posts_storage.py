from datetime import datetime

from loguru import logger
from sqlalchemy import func
from telethon.tl.types import Message

from models import ChannelModel, ChannelType, MessageModel

MESSAGE_ID = int


class NoNewPosts(Exception):
    """Post storage raise this exception when there are no new posts"""


class PostStorage:
    def __init__(self, session_maker) -> None:
        logger.info("Post storage is initializing...")
        self.session_maker = session_maker

    async def post(self, message: Message) -> None:
        with self.session_maker() as session:
            channel_id = message.fwd_from.from_id.channel_id
            channel = session.query(ChannelModel).filter_by(channel_id=channel_id).first()
            if not channel:
                channel_type = ChannelModel.check_channel_type(channel_id)
                channel = ChannelModel(channel_id=channel_id, channel_type=channel_type)
                session.add(channel)
                session.commit()
                logger.info(f"New channel added: {channel}")

            message = MessageModel(
                message_id=message.id,
                grouped_id=message.grouped_id,
                channel_id=channel_id,
            )
            session.add(message)
            logger.info("Commiting changes")
            session.commit()

    def get_oldest_unsent_post(self, channel_type_filter=None) -> list[MESSAGE_ID]:
        with self.session_maker() as session:
            first_unsent_id = (
                session.query(func.min(MessageModel.id)).filter(MessageModel.sent.is_(None)).scalar_subquery()
            )
            first_unsent_message = session.query(MessageModel).filter(MessageModel.id == first_unsent_id).first()

            if not first_unsent_message:
                raise NoNewPosts("No new posts in the storage")

            if channel_type_filter:
                channel = (
                    session.query(ChannelModel)
                    .filter(ChannelModel.channel_id == first_unsent_message.channel_id)
                    .first()
                )

                if not channel:
                    raise NoNewPosts("No corresponding channel found for the message")

                if channel_type_filter == "news" and channel.channel_type != ChannelType.NEWS.value:
                    raise NoNewPosts("No new posts of type 'news'")
                elif channel_type_filter == "fun" and channel.channel_type != ChannelType.FUN.value:
                    raise NoNewPosts("No new posts of type 'fun'")

            if first_unsent_message.grouped_id is not None:
                messages = (
                    session.query(MessageModel.message_id)
                    .filter(MessageModel.grouped_id == first_unsent_message.grouped_id)
                    .all()
                )
                return [msg.message_id for msg in messages]

            return [first_unsent_message.message_id]

    def set_sent_multiple(self, message_ids: list[int]) -> None:
        with self.session_maker() as session:
            session.query(MessageModel).filter(MessageModel.message_id.in_(message_ids)).update(
                {MessageModel.sent: datetime.now()}
            )
            session.commit()
