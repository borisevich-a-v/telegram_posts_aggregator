from asyncio import QueueEmpty

from loguru import logger
from telethon import TelegramClient, events
from telethon.sessions import StringSession

from src.config import ADMIN, AGGREGATOR_CHANNEL, BOT_SESSION, TELEGRAM_API_HASH, TELEGRAM_API_ID, TELEGRAM_BOT_TOKEN
from src.posts_storage import PostQueue


def create_bot(queue: PostQueue) -> TelegramClient:
    bot = TelegramClient(StringSession(BOT_SESSION), TELEGRAM_API_ID, TELEGRAM_API_HASH).start(
        bot_token=TELEGRAM_BOT_TOKEN
    )

    @bot.on(events.NewMessage(chats=AGGREGATOR_CHANNEL))
    async def aggregator_channel_listener(event):
        if hasattr(event, "message"):
            await queue.put(event.message)
        else:
            logger.critical("No message", event)

    @bot.on(events.NewMessage(pattern="/next", from_users=ADMIN))
    async def handle_next_command(event):
        try:
            msg = queue.get_nowait()
            await event.client.forward_messages(ADMIN, msg)
        except QueueEmpty:
            await event.reply("No updates")

    bot.start()
    logger.info("Bot has been initialized")
    return bot
