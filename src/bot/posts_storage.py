from asyncio import Queue

from telethon.tl.types import Message

MESSAGE_GROUP_ID = int


class PostQueue:
    """
    Async queue that gather grouped messages into one queue message
    """

    def __init__(self) -> None:
        self._queue: Queue[Message | MESSAGE_GROUP_ID] = Queue()
        self._grouped_messages: dict[MESSAGE_GROUP_ID, list[Message]] = {}

    async def put(self, message: Message) -> None:
        if message.grouped_id:
            await self._put_message_with_grouped_id(message)
            return

        await self._queue.put(message)

    async def _put_message_with_grouped_id(self, message: Message) -> None:
        grouped_id = message.grouped_id

        if group := self._grouped_messages.get(grouped_id):
            group.append(message)
            return

        self._grouped_messages[grouped_id] = [message]
        await self._queue.put(grouped_id)

    def get_nowait(self) -> list[Message]:
        """
        Return list of messages with the same `grouped_id` or raise `QueueEmpty` if the queue is empty
            Raises: QueueEmpty
        """
        queue_obj = self._queue.get_nowait()
        if isinstance(queue_obj, Message):
            return [queue_obj]
        elif isinstance(queue_obj, int):
            return self._grouped_messages.pop(queue_obj)
        else:
            raise TypeError(f"Unexpected type of object in the queue: {type(queue_obj)}. Value: {queue_obj}")
