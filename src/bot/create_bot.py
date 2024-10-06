import re

from loguru import logger
from telethon import TelegramClient, events
from telethon.sessions import StringSession

from config import ADMIN, AGGREGATOR_CHANNEL, TELEGRAM_API_HASH, TELEGRAM_API_ID, TELEGRAM_BOT_TOKEN
from models import ChannelType as ch_tp
from telegram_slow_client import TelegramSlowClient

from .posts_storage import NoNewPosts, PostStorage
from .warden.warden import NotAllowed, Warden


def create_bot(post_storage: PostStorage, warden: Warden) -> TelegramClient:
    logger.info("Creating bot")
    bot = TelegramSlowClient(StringSession(), TELEGRAM_API_ID, TELEGRAM_API_HASH, min_request_interval=0.005).start(
        bot_token=TELEGRAM_BOT_TOKEN
    )

    @bot.on(events.NewMessage(chats=AGGREGATOR_CHANNEL))
    async def aggregator_channel_listener(event) -> None:
        if hasattr(event, "message"):
            await post_storage.post(event.message)
        else:
            logger.critical("No message", event)

    @bot.on(events.NewMessage(pattern=rf"/next({ch_tp.FUN.value}|{ch_tp.NEWS.value})?(\d+)?", from_users=ADMIN))
    async def handle_next_command(event) -> None:
        logger.info(f"Got {event.pattern_match} request from Admin")
        try:
            pattern = event.pattern_match.group(1) if True else None
            amount_str = event.pattern_match.group(2)
            amount = int(amount_str) if amount_str.isdigit() else 1
        except (ValueError, IndexError) as exp:
            await event.reply(f"Bad request format: {exp}")
            return

        for i in range(amount):

            try:
                warden.check_allowance()
            except NotAllowed as exp:
                logger.info("User is not allowed to read a new message %s", str(exp))
                await event.reply(str(exp))
                return

            try:
                msgs = post_storage.get_oldest_unsent_post(channel_type_filter=pattern)
                await event.client.forward_messages(entity=ADMIN, messages=msgs, from_peer=AGGREGATOR_CHANNEL)
                post_storage.set_sent_multiple(msgs)
            except NoNewPosts:
                await event.reply("No updates")
                return

    bot.start()
    logger.info("Bot has been initialized")
    return bot
