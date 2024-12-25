import asyncio
from typing import NoReturn

from loguru import logger
from telethon import TelegramClient, events
from telethon.sessions import StringSession
from telethon.utils import get_peer_id

from aggregator.config import (
    AGGREGATOR_CHANNEL,
    CLIENT_SESSION,
    TELEGRAM_API_HASH,
    TELEGRAM_API_ID,
    UPDATE_WHITELISTED_CHANNELS_INTERVAL,
)
from aggregator.posts_storage import PostStorage

FORWARDING_MESSAGE_LOCK = asyncio.Lock()


async def continuously_update_channel_listeners(
    client: TelegramClient,
    post_storage: PostStorage,
) -> NoReturn:
    async def public_channel_listener(event) -> None:
        """
        This handler just forward messages to the aggregation channel.
        The bot can't access some posts from other public channel, so we forward posts to the place where bot can
        access them.
        """
        if hasattr(event, "message"):
            # probably it's a place for improvement.
            # IDK how to forward grouped messages together if only process separated messages, but not album.
            logger.debug("Processing a single message event...")
            is_single_message = True
            messages = [event.message]
            await asyncio.sleep(2)

        elif hasattr(event, "messages"):
            logger.debug("Processing a multi message event...")
            is_single_message = False
            messages = event.messages

        else:
            logger.debug("Not a message")
            return

        async with FORWARDING_MESSAGE_LOCK:
            if post_storage.is_duplicate(messages):
                logger.warning("The messages have been saved previously: {}", messages)
                return
            logger.info("New messages {} will be forwarded into the aggregation channel", messages)
            fwd_event = await event.forward_to(AGGREGATOR_CHANNEL)

            first_message = fwd_event if is_single_message else fwd_event[0]
            fwd_messages = [fwd_event] if is_single_message else fwd_event

            original_channel_id = get_peer_id(first_message.fwd_from.from_id)
            forwarded_from_channel_id = get_peer_id(messages[0].peer_id)

            for fwd_msg, msg in zip(fwd_messages, messages):
                post_storage.post(
                    fwd_msg.id,
                    msg.grouped_id,
                    forwarded_from_channel_id,
                    original_channel_id,
                    fwd_msg.fwd_from.channel_post,
                )
        logger.debug("Messages was successfully processed")

    while True:
        logger.debug("Updating channels to listen.")
        whitelisted_channels = post_storage.get_whitelisted_channel_ids()
        message_event = events.NewMessage(whitelisted_channels)
        album_event = events.Album(whitelisted_channels)

        client.add_event_handler(public_channel_listener, album_event)
        client.add_event_handler(public_channel_listener, message_event)

        await asyncio.sleep(UPDATE_WHITELISTED_CHANNELS_INTERVAL)

        client.remove_event_handler(public_channel_listener, album_event)
        client.remove_event_handler(public_channel_listener, message_event)


async def create_telegram_agent(post_storage: PostStorage) -> tuple[TelegramClient, asyncio.Task]:
    logger.info("Creating telegram agent")
    client = TelegramClient(StringSession(CLIENT_SESSION), TELEGRAM_API_ID, TELEGRAM_API_HASH)

    listener_updater = asyncio.create_task(continuously_update_channel_listeners(client, post_storage))

    await client.start()
    logger.info("Client has been initialized")
    return client, listener_updater
