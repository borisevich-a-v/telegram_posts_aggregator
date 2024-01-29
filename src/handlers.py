from asyncio import Queue, QueueEmpty

from loguru import logger
from telethon import events

from .config import ADMIN, AGGREGATOR_CHANNEL, FUN_CHANNELS, NEWS_CHANNELS

new_posts: Queue = Queue()


def get_next_post():
    try:
        return new_posts.get_nowait()
    except QueueEmpty:
        return None


@events.register(events.NewMessage(chats=FUN_CHANNELS + NEWS_CHANNELS))
async def public_channel_listener(event):
    logger.info(f"New message from `{event.message.chat.title}`")
    await event.client.forward_messages(AGGREGATOR_CHANNEL, event.message)


@events.register(events.NewMessage(chats=AGGREGATOR_CHANNEL))
async def aggregator_channel_listener(event):
    """
    This handler listen aggregation channel. For some reason bot can't access some posts
    from other public channel
    """
    logger.debug(f"Put message {event.message}")
    await new_posts.put(event.message)
    logger.debug(f"Message have been put")


@events.register(events.NewMessage(pattern="/next"))
async def handle_next_command(event):
    sender = await event.get_sender()
    if sender.username != ADMIN:
        logger.warning("No admin user tries to get a message")
        return

    if msg := get_next_post():
        logger.debug(f"Sending new content to a {sender.username}")
        logger.debug(f"Content {msg}")

        await event.client.forward_messages(sender, msg)

    else:
        logger.debug("Sending `no updates`")
        await event.reply("No updates")
