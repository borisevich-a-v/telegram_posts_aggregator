from loguru import logger
from telethon import TelegramClient, events
from telethon.sessions import StringSession

from bot.warden.warden import NotAllowed, Warden
from config import ADMIN, AGGREGATOR_CHANNEL, TELEGRAM_API_HASH, TELEGRAM_API_ID, TELEGRAM_BOT_TOKEN
from models import ChannelType
from posts_storage import NoNewPosts, PostStorage
from telegram_slow_client import TelegramSlowClient


def create_bot(post_storage: PostStorage, warden: Warden) -> TelegramClient:
    logger.info("Creating bot")
    bot = TelegramSlowClient(StringSession(), TELEGRAM_API_ID, TELEGRAM_API_HASH, min_request_interval=0.005).start(
        bot_token=TELEGRAM_BOT_TOKEN
    )

    @bot.on(events.NewMessage(chats=AGGREGATOR_CHANNEL))
    async def aggregator_channel_listener(event) -> None:
        if hasattr(event, "message"):
            post_storage.post(event.message)
        else:
            logger.critical("No message {}", event)

    @bot.on(events.NewMessage(pattern=rf"/({'|'.join(t for t in ChannelType)})(\d{{0,5}})", from_users=ADMIN))
    async def handle_posts_request_command(event) -> None:
        logger.info(f"Got {event.pattern_match} request from Admin")

        try:
            channel_type = ChannelType(event.pattern_match.group(1))
            if channel_type is ChannelType.ALL:
                channel_type = None
        except (ValueError, IndexError) as exp:
            await event.reply(f"Bad request format: {exp}")
            return

        amount = int(event.pattern_match.group(2) or "1")
        if amount > 100:
            amount = 100
            await event.reply("Can't send more than 100 posts in one shot")

        for i in range(amount):

            try:
                warden.check_allowance()
            except NotAllowed as exp:
                logger.info("User is not allowed to read a new message %s", str(exp))
                await event.reply(str(exp))
                return

            try:
                msgs = post_storage.get_oldest_unsent_post(channel_type)
                await event.client.forward_messages(entity=ADMIN, messages=msgs, from_peer=AGGREGATOR_CHANNEL)
                post_storage.set_sent_multiple(msgs)
            except NoNewPosts:
                await event.reply("No updates")
                return

    bot.start()
    logger.info("Bot has been initialized")
    return bot
