import asyncio

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
from aggregator.openai_driver import OpenaiDriver
from aggregator.posts_storage import PostStorage

FORWARDING_MESSAGE_LOCK = asyncio.Lock()


async def handle_single_message_event(event, post_storage: PostStorage, openai_driver: OpenaiDriver):
    # sleep to let album be the first, as album can be forwarded as a group.
    await asyncio.sleep(2)
    message = event.message

    async with FORWARDING_MESSAGE_LOCK:
        if await post_storage.is_duplicate([message]):
            logger.info("The message have been saved previously: {}", message.id)
            return
        logger.info("New messages {} will be forwarded into the aggregation channel", message)

        fwd_event, embedding = await asyncio.gather(
            event.forward_to(AGGREGATOR_CHANNEL), openai_driver.get_embedding(message.message)
        )

        await post_storage.post(
            tg_message_id=fwd_event.id,
            grouped_id=message.grouped_id,
            event_peer_id=get_peer_id(message.peer_id),
            original_channel_id=get_peer_id(fwd_event.fwd_from.from_id),
            original_message_id=fwd_event.fwd_from.channel_post,
            embedding=embedding,
        )


async def handle_album_event(event, post_storage: PostStorage, openai_driver: OpenaiDriver):
    messages = event.messages
    async with FORWARDING_MESSAGE_LOCK:
        if await post_storage.is_duplicate(messages):
            logger.info("The messages have been saved previously: {}", messages)
            return
        logger.debug("New messages {} will be forwarded into the aggregation channel", messages)

        fwd_event, is_embedding_exist = await asyncio.gather(
            event.forward_to(AGGREGATOR_CHANNEL), post_storage.is_group_processed(messages[0].grouped_id)
        )

        for fwd_msg, msg in zip(fwd_event, messages):
            if msg.message and msg.message.strip() and not is_embedding_exist:
                embedding = await openai_driver.get_embedding(msg.message)
            else:
                embedding = None

            await post_storage.post(
                tg_message_id=fwd_msg.id,
                grouped_id=msg.grouped_id,
                event_peer_id=get_peer_id(messages[0].peer_id),
                original_channel_id=get_peer_id(fwd_msg.fwd_from.from_id),
                original_message_id=fwd_msg.fwd_from.channel_post,
                embedding=embedding,
            )


async def handle_event(event, post_storage: PostStorage, openai_driver: OpenaiDriver) -> None:
    """
    Process an event.
    Event can be a single message, or multiple grouped messages (as Telegram handle every image as an
    independent messages). In grouped messages only one of them can have textual information.
    Sometimes grouped message can be lost, so we check if we registered it.
    """
    if hasattr(event, "message"):
        logger.debug("Processing a single message event...")
        await handle_single_message_event(event, post_storage, openai_driver)
    elif hasattr(event, "messages"):
        logger.debug("Processing a multi message event...")
        await handle_album_event(event, post_storage, openai_driver)
    else:
        logger.debug("Not a message")
        return
    logger.debug("Messages was successfully processed")


async def continuously_update_channel_listeners(
    client: TelegramClient,
    post_storage: PostStorage,
    openai_driver: OpenaiDriver,
):
    async def public_channel_listener(event) -> None:
        """
        This handler just forward messages to the aggregation channel.
        The bot can't access some posts from other public channel, so we forward posts to the place where bot can
        access them.
        """
        await handle_event(event, post_storage, openai_driver)

    while True:
        logger.debug("Updating channels to listen.")
        whitelisted_channels = await post_storage.get_whitelisted_channel_ids()
        message_event = events.NewMessage(whitelisted_channels)
        album_event = events.Album(whitelisted_channels)

        client.add_event_handler(public_channel_listener, album_event)
        client.add_event_handler(public_channel_listener, message_event)

        await asyncio.sleep(UPDATE_WHITELISTED_CHANNELS_INTERVAL)

        client.remove_event_handler(public_channel_listener, album_event)
        client.remove_event_handler(public_channel_listener, message_event)


async def create_telegram_agent(
    post_storage: PostStorage, openai_driver: OpenaiDriver
) -> tuple[TelegramClient, asyncio.Task]:
    logger.info("Creating telegram agent")
    client = TelegramClient(StringSession(CLIENT_SESSION), TELEGRAM_API_ID, TELEGRAM_API_HASH)

    listener_updater = asyncio.create_task(continuously_update_channel_listeners(client, post_storage, openai_driver))

    await client.start()
    logger.info("Client has been initialized")
    return client, listener_updater
