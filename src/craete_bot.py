from asyncio import QueueEmpty

from loguru import logger
from telethon import TelegramClient, events
from telethon.sessions import StringSession

from src.config import ADMIN, AGGREGATOR_CHANNEL, TELEGRAM_API_HASH, TELEGRAM_API_ID, TELEGRAM_BOT_TOKEN
from src.posts_storage import PostQueue
from src.warden.warden import NotAllowed, Warden


def create_bot(queue: PostQueue, warden: Warden) -> TelegramClient:
    logger.info("Creating bot")
    bot = TelegramClient(StringSession(), TELEGRAM_API_ID, TELEGRAM_API_HASH).start(bot_token=TELEGRAM_BOT_TOKEN)

    @bot.on(events.NewMessage(chats=AGGREGATOR_CHANNEL))
    async def aggregator_channel_listener(event) -> None:
        if hasattr(event, "message"):
            await queue.put(event.message)
        else:
            logger.critical("No message", event)

    @bot.on(events.NewMessage(pattern="/next", from_users=ADMIN))
    async def handle_next_command(event) -> None:
        logger.info("Got `/next` request from Admin")
        try:
            warden.check_allowance()
        except NotAllowed as exp:
            logger.info("User is not allowed to read a new message %s", str(exp))
            await event.reply(str(exp))
            return

        try:
            msg = queue.get_nowait()
            await event.client.forward_messages(ADMIN, msg)
        except QueueEmpty:
            await event.reply("No updates")

    bot.start()
    logger.info("Bot has been initialized")
    return bot
