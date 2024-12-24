from sqlalchemy import BigInteger, Column, DateTime, ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()

NOT_SPECIFIED_CHANNEL_TYPE = "__NOT_SPECIFIED_TYPE"


class MessageModel(Base):
    __tablename__ = "message"

    id = Column(Integer, primary_key=True)
    message_id = Column(Integer, nullable=False)  # message id in the aggr channel
    grouped_id = Column(BigInteger, nullable=True)  # grouped_id is a Telegram hack to group messages
    channel_id = Column(BigInteger, ForeignKey("channel.id"), nullable=False)  # source channel id.
    sent = Column(DateTime, nullable=True)  # have the message been sent to the user. NULL if it haven't been sent
    original_message_id = Column(Integer, nullable=False)  # Message id in a source channel. for deduplicate reposts

    channel = relationship("ChannelModel", back_populates="messages")

    __table_args__ = (
        # Every message in a telegram channel has unique id, so the pair original_message_id
        # and (original) channel_id should be uniq
        UniqueConstraint("original_message_id", "channel_id", name="source_message_uniq"),
    )

    def __repr__(self):
        return f"MessageModel({self.id, self.message_id, self.grouped_id, self.channel_id, self.sent, self.original_message_id})"


class ChannelModel(Base):
    __tablename__ = "channel"

    id = Column(BigInteger, primary_key=True)  # telegram channel id
    type_id = Column(Integer, ForeignKey("channel_type.id"), default=0)  # 0 is `NOT_SPECIFIED_CHANNEL_TYPE`
    name = Column(String, nullable=True)

    messages = relationship("MessageModel", back_populates="channel")
    type_ = relationship("ChannelTypeModel", back_populates="channels")

    def __repr__(self):
        return f"ChannelModel({self.id, self.type_id, self.name})"


class ChannelTypeModel(Base):
    __tablename__ = "channel_type"

    id = Column(Integer, primary_key=True)
    type_ = Column(String, nullable=False, default=NOT_SPECIFIED_CHANNEL_TYPE, unique=True)

    channels = relationship("ChannelModel", back_populates="type_")

    def __repr__(self):
        return f"ChannelTypeModel({self.id, self.type_})"
