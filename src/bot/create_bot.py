import re

from loguru import logger
from telethon import TelegramClient, events
from telethon.sessions import StringSession
from typing_extensions import NamedTuple

from bot.warden.warden import NotAllowed, Warden
from config import ADMIN, AGGREGATOR_CHANNEL, TELEGRAM_API_HASH, TELEGRAM_API_ID, TELEGRAM_BOT_TOKEN
from posts_storage import NoNewPosts, PostStorage
from telegram_slow_client import TelegramSlowClient

ANY_CHANNEL_COMMAND = "next"


class PostRequestError(Exception):
    """This error represents any problem with new posts request"""


class PostRequest(NamedTuple):
    channel_type: str | None
    amount: int

    @classmethod
    def from_event(cls, event):
        channel_type = event.pattern_match.group(1)
        if channel_type is None:
            raise PostRequestError("Bad request format. Can't parse requested channel type")
        if channel_type == ANY_CHANNEL_COMMAND:
            channel_type = None

        amount = int(event.pattern_match.group(2) or "1")
        if amount > 100:
            amount = 100

        return cls(channel_type, amount)


def get_request_pattern(post_storage: PostStorage) -> re.Pattern:
    type_pattern = f"({'|'.join(t for t in (post_storage.get_all_custom_channel_types() + [ANY_CHANNEL_COMMAND]))})"
    amount_pattern = rf"(\d{{0,5}})"
    return re.compile(rf"/{type_pattern}{amount_pattern}")


def create_bot(post_storage: PostStorage, warden: Warden) -> TelegramClient:
    logger.info("Creating bot")
    bot = TelegramSlowClient(StringSession(), TELEGRAM_API_ID, TELEGRAM_API_HASH, min_request_interval=0.005).start(
        bot_token=TELEGRAM_BOT_TOKEN
    )

    # TODO: should we parse album here?
    @bot.on(events.NewMessage(chats=AGGREGATOR_CHANNEL))
    async def aggregator_channel_listener(event) -> None:
        if hasattr(event, "message"):
            post_storage.post(event.message)
        else:
            logger.critical("No message {}", event)

    @bot.on(events.NewMessage(pattern=get_request_pattern(post_storage), from_users=ADMIN))
    async def handle_posts_request_command(event) -> None:
        logger.info(f"Got {event.pattern_match} request from Admin")

        try:
            request = PostRequest.from_event(event)
        except PostRequestError as exp:
            await event.reply(str(exp))
            return

        for _ in range(request.amount):
            try:
                warden.check_allowance()
                pass
            except NotAllowed as exp:
                await event.reply(str(exp))
                return

            try:
                msgs = post_storage.get_oldest_unsent_post(request.channel_type)
                await event.client.forward_messages(entity=ADMIN, messages=msgs, from_peer=AGGREGATOR_CHANNEL)
                post_storage.set_sent_multiple(msgs)
            except NoNewPosts:
                await event.reply("No updates")
                return

    bot.start()
    logger.info("Bot has been initialized")
    return bot
