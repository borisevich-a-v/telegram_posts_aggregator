from enum import Enum

from sqlalchemy import BigInteger, Boolean, Column, DateTime
from sqlalchemy import Enum as SQL_Enum
from sqlalchemy import ForeignKey, Integer, UniqueConstraint
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()


class ChannelType(Enum):
    FUN = 1
    NEWS = 2


class MessageModel(Base):
    __tablename__ = "message"

    id = Column(Integer, primary_key=True)
    message_id = Column(Integer, nullable=False)
    grouped_id = Column(BigInteger, nullable=True)
    channel_id = Column(BigInteger, ForeignKey("channel.channel_id"), nullable=False)
    sent = Column(DateTime, nullable=True)

    channel = relationship("ChannelModel", back_populates="message")

    def repr(self):
        return f"MessageModel({self.id, self.message_id, self.grouped_id, self.sent})"


class ChannelModel(Base):
    __tablename__ = "channel"

    channel_id = Column(BigInteger, primary_key=True)
    channel_type = Column(SQL_Enum(ChannelType), nullable=True)

    message = relationship("MessageModel", back_populates="channel")

    def repr(self):
        return f"ChannelModel({self.channel_id, self.channel_type})"

    @staticmethod
    def check_channel_type(channel_id):
        channel_dict = {"NEWS": ["1190042072"], "FUN": ["1009232144", "1148195583"]}

        for channel_type, channel_ids in channel_dict.items():
            if str(channel_id) in channel_ids:
                return channel_type
