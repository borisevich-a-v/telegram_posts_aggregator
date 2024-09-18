from typing import Iterable, NamedTuple

from loguru import logger
from telethon.tl.types import Message, TypePeer


class MessageUniqueKey(NamedTuple):
    peer_id: int
    message_id: int


class MessagesRegister:
    MIN_NUMBER_OF_STORED_MESSAGE_IDS = 50

    def __init__(self) -> None:
        logger.info("Message register is initializing")
        self.last_messages_sets: list[set[MessageUniqueKey]] = [set(), set()]

    def add(self, message: Message) -> None:
        populating_set = self.last_messages_sets[1]
        populating_set.add(self._form_message_unique_key(message))

        if len(populating_set) > self.MIN_NUMBER_OF_STORED_MESSAGE_IDS:
            self._rotate_messages()

    def update(self, messages: Iterable[Message]) -> None:
        for msg in messages:
            self.add(msg)

    def remove(self, message: Message) -> None:
        for s in self.last_messages_sets:
            try:
                s.remove(self._form_message_unique_key(message))
            except KeyError:
                pass

    def remove_many(self, messages: Iterable[Message]) -> None:
        for msg in messages:
            self.remove(msg)

    def __contains__(self, message: Message):
        for messages_sets in self.last_messages_sets:
            if self._form_message_unique_key(message) in messages_sets:
                return True
        return False

    def _rotate_messages(self):
        self.last_messages_sets.pop(0)
        self.last_messages_sets.append(set())

    def _form_message_unique_key(self, message: Message) -> MessageUniqueKey:
        return MessageUniqueKey(self._get_peer_id(message.peer_id), message.id)

    def _get_peer_id(self, peer: TypePeer) -> int:
        """Assume that we listen channels only"""
        return peer.channel_id
