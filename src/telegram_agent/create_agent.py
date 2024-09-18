from loguru import logger
from telethon import TelegramClient, events
from telethon.sessions import StringSession

from config import AGGREGATOR_CHANNEL, CLIENT_SESSION, FUN_CHANNELS, NEWS_CHANNELS, TELEGRAM_API_HASH, TELEGRAM_API_ID

from .registered_messages import MessagesRegister


def create_telegram_agent(registered_messages: MessagesRegister) -> TelegramClient:
    logger.info("Creating telegram agent")
    client = TelegramClient(StringSession(CLIENT_SESSION), TELEGRAM_API_ID, TELEGRAM_API_HASH)

    @client.on(events.NewMessage(AGGREGATOR_CHANNEL, blacklist_chats=True))
    @client.on(events.Album(AGGREGATOR_CHANNEL, blacklist_chats=True))
    async def public_channel_listener(event) -> None:
        """
        This handler just forward messages to the aggregation channel.
        The bot can't access some posts from other public channel, so we forward posts to the place where bot can
        access them.
        """
        if hasattr(event, "messages") and event.grouped_id:
            if all(msg in registered_messages for msg in event.messages):
                logger.info("Event (album) is already processed")
                return

            registered_messages.update(event.messages)
            await event.forward_to(AGGREGATOR_CHANNEL)
            logger.info(f"Got new post {[m.id for m in event.messages]} and have added it to the aggregation channel")

        if hasattr(event, "message") and not event.grouped_id:
            if event.message in registered_messages:
                logger.info("Event (message) is already processed")
                return

            registered_messages.add(event.message)
            await event.forward_to(AGGREGATOR_CHANNEL)
            logger.info(f"Got new post {event.message.id} and have added it to the aggregation channel")

    client.start()
    logger.info("Client has been initialized")
    return client
