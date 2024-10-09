from enum import Enum

from sqlalchemy import BigInteger, Boolean, Column, DateTime, ForeignKey, Integer, UniqueConstraint
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()


class ChannelType(Enum):
    FUN = 1
    NEWS = 2


class MessageModel(Base):
    __tablename__ = "message"

    id = Column(Integer, primary_key=True)
    message_id = Column(Integer, nullable=False)  # message id in the aggr channel
    grouped_id = Column(BigInteger, nullable=True)  # grouped_id is a Telegram hack to group messages
    channel_id = Column(BigInteger, ForeignKey("channel.channel_id"), nullable=False)  # source channel id
    sent = Column(DateTime, nullable=True)  # have the message been sent to the user
    original_message_id = Column(Integer, nullable=False)  # for deduplicate reposts

    channel = relationship("ChannelModel", back_populates="messages")

    __table_args__ = (
        # Every message in a telegram channel has unique id
        UniqueConstraint("original_message_id", "channel_id", name="_customer_location_uc"),
    )

    def __repr__(self):
        return f"MessageModel({self.id, self.message_id, self.grouped_id, self.sent})"


class ChannelModel(Base):
    __tablename__ = "channel"

    channel_id = Column(BigInteger, primary_key=True)
    channel_type = Column(Integer, nullable=True)

    messages = relationship("MessageModel", back_populates="channel")

    def __repr__(self):
        return f"ChannelModel({self.channel_id, self.channel_type})"
