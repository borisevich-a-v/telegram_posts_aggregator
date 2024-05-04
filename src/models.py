from sqlalchemy import BigInteger, Column, DateTime, Integer
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class MessageModel(Base):
    __tablename__ = "messages"

    id = Column(Integer, primary_key=True)
    message_id = Column(Integer, nullable=False)
    grouped_id = Column(BigInteger, nullable=True)
    sent = Column(DateTime, nullable=True)

    def __repr__(self):
        return f"MessageModel({self.id, self.message_id, self.grouped_id, self.sent})"
