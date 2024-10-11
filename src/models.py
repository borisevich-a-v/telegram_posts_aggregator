import enum

from sqlalchemy import BigInteger, Column, DateTime, ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()


class ChannelType(enum.StrEnum):
    FUN = "fun"
    NEWS = "news"


class MessageModel(Base):
    __tablename__ = "message"

    id = Column(Integer, primary_key=True)
    message_id = Column(Integer, nullable=False)  # message id in the aggr channel
    grouped_id = Column(BigInteger, nullable=True)  # grouped_id is a Telegram hack to group messages
    channel_id = Column(BigInteger, ForeignKey("channel.id"), nullable=False)  # source channel id
    sent = Column(DateTime, nullable=True)  # have the message been sent to the user
    original_message_id = Column(Integer, nullable=False)  # for deduplicate reposts

    channel = relationship("ChannelModel", back_populates="messages")

    __table_args__ = (
        # Every message in a telegram channel has unique id, so the pair message_id and channel_id should be uniq
        UniqueConstraint("original_message_id", "channel_id", name="source_message_uniq"),
    )

    def __repr__(self):
        return f"MessageModel({self.id, self.message_id, self.grouped_id, self.sent})"


class ChannelModel(Base):
    __tablename__ = "channel"

    id = Column(BigInteger, primary_key=True)
    type = Column(String, nullable=True)
    name = Column(String, nullable=True)

    messages = relationship("MessageModel", back_populates="channel")

    def __repr__(self):
        return f"ChannelModel({self.id, self.type, self.name})"
