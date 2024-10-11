from loguru import logger
from telethon import TelegramClient, events
from telethon.sessions import StringSession

from config import AGGREGATOR_CHANNEL, CLIENT_SESSION, TELEGRAM_API_HASH, TELEGRAM_API_ID
from posts_storage import PostStorage
from telegram_slow_client import TelegramSlowClient


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
            if post_storage.is_original_msg_duplicate(event.messages):
                logger.warning("The messages have been saved previously: {}", event.messages)
                return

            await event.forward_to(AGGREGATOR_CHANNEL)
            logger.info("Got a new post {} and added it to the aggregation channel", [m.id for m in event.messages])

        if hasattr(event, "message") and not event.grouped_id:
            if post_storage.is_original_msg_duplicate([event.message]):
                logger.warning("The messages have been saved previously: {}", event.message)
                return

            await event.forward_to(AGGREGATOR_CHANNEL)
            logger.info(f"Got new post {event.message.id} and have added it to the aggregation channel")

    client.start()
    logger.info("Client has been initialized")
    return client
