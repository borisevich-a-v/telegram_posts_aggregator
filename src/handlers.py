from asyncio import QueueEmpty

from loguru import logger
from telethon import events

from .config import ADMIN, AGGREGATOR_CHANNEL, FUN_CHANNELS, NEWS_CHANNELS
from .posts_storage import PostQueue

queue = PostQueue()


@events.register(events.NewMessage(chats=FUN_CHANNELS + NEWS_CHANNELS))
async def public_channel_listener(event):
    """
    This handler just forward messages to the aggregation channel. For some reason bot can't access some
     posts from other public channel.
    """
    logger.info(event)
    logger.info(event.message)
    await event.client.forward_messages(AGGREGATOR_CHANNEL, event.message)


@events.register(events.NewMessage(chats=AGGREGATOR_CHANNEL))
async def aggregator_channel_listener(event):
    await queue.put(event.message)


@events.register(events.NewMessage(pattern="/next", from_users=ADMIN))
async def handle_next_command(event):
    try:
        msg = queue.get_nowait()
        logger.debug(f"Content {msg}")
        await event.client.forward_messages(ADMIN, msg)
    except QueueEmpty:
        await event.reply("No updates")
