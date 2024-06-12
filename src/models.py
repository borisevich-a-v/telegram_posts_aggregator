from enum import Enum

from sqlalchemy import BigInteger, Boolean, Column, DateTime, ForeignKey, Integer, UniqueConstraint
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()


class ChannelType(Enum):
    FUN = 1
    NEWS = 2


class MessageModel(Base):
    __tablename__ = "messages"

    id = Column(Integer, primary_key=True)
    message_id = Column(Integer, nullable=False)
    grouped_id = Column(BigInteger, nullable=True)
    channel_id = Column(BigInteger, ForeignKey("channels.channel_id"), nullable=True)
    sent = Column(DateTime, nullable=True)

    channel = relationship("ChannelsModel", back_populates="messages")

    def repr(self):
        return f"MessageModel({self.id, self.message_id, self.grouped_id, self.sent})"


class ChannelsModel(Base):
    __tablename__ = "channels"

    channel_id = Column(BigInteger, nullable=False, unique=True, primary_key=True)
    channel_type = Column(Integer, nullable=True)

    messages = relationship("MessageModel", back_populates="channel")
