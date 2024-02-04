from loguru import logger
from telethon import TelegramClient, events
from telethon.sessions import StringSession

from .config import AGGREGATOR_CHANNEL, CLIENT_SESSION, FUN_CHANNELS, NEWS_CHANNELS, TELEGRAM_API_HASH, TELEGRAM_API_ID


def create_client() -> TelegramClient:
    client = TelegramClient(StringSession(CLIENT_SESSION), TELEGRAM_API_ID, TELEGRAM_API_HASH)

    @client.on(events.NewMessage(chats=FUN_CHANNELS + NEWS_CHANNELS))
    async def public_channel_listener(event):
        """
        This handler just forward messages to the aggregation channel.
        For some reason bot can't access some posts from other public channel, so we forward posts to the place
        where bot can access them
        """
        await event.client.forward_messages(AGGREGATOR_CHANNEL, event.message)
        logger.info(f"Got new post {event.message.id} and have added it to the aggregation channel")

    client.start()
    logger.info("Client has been initialized")
    return client
