from loguru import logger
from telethon import TelegramClient, events
from telethon.sessions import StringSession
from telethon.tl.types import Message, PeerUser

from aggregator.config import AGGREGATOR_CHANNEL, CLIENT_SESSION, TELEGRAM_API_HASH, TELEGRAM_API_ID
from aggregator.posts_storage import PostStorage
from aggregator.telegram_slow_client import TelegramSlowClient


def is_it_user(message: Message) -> bool:
    from_id = message.from_id
    if isinstance(from_id, (PeerUser,)):
        return True
    return False


def create_telegram_agent(post_storage: PostStorage) -> TelegramClient:
    logger.info("Creating telegram agent")
    client = TelegramSlowClient(
        StringSession(CLIENT_SESSION), TELEGRAM_API_ID, TELEGRAM_API_HASH, min_request_interval=3
    )

    @client.on(events.NewMessage(AGGREGATOR_CHANNEL, blacklist_chats=True))
    @client.on(events.Album(AGGREGATOR_CHANNEL, blacklist_chats=True))
    async def public_channel_listener(event) -> None:
        """
        This handler just forward messages to the aggregation channel.
        The bot can't access some posts from other public channel, so we forward posts to the place where bot can
        access them.
        """
        if hasattr(event, "messages") and event.grouped_id:
            messages = event.messages
        elif hasattr(event, "message") and not event.grouped_id:
            messages = [event.message]
        else:
            logger.info("Got an update, that is not a message. Skipped.")
            return

        if is_it_user(messages[0]):
            return

        if post_storage.is_original_msg_duplicate(messages):
            logger.warning("The messages have been saved previously: {}", messages)
            return

        await event.forward_to(AGGREGATOR_CHANNEL)
        logger.info("Got a new post {} and added it to the aggregation channel", [m.id for m in event.messages])

    client.start()
    logger.info("Client has been initialized")
    return client
