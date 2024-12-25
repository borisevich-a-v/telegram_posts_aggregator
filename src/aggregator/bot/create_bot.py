import re

from loguru import logger
from telethon import TelegramClient, events
from telethon.sessions import StringSession
from telethon.utils import get_display_name
from typing_extensions import NamedTuple

from aggregator.bot.warden.warden import NotAllowed, Warden
from aggregator.config import (
    ADMIN,
    AGGREGATOR_CHANNEL,
    BOT_SESSION,
    TELEGRAM_API_HASH,
    TELEGRAM_API_ID,
    UPDATE_WHITELISTED_CHANNELS_INTERVAL,
)
from aggregator.posts_storage import NoNewPosts, PostStorage

ANY_CHANNEL_COMMAND = "next"
ADD_CHANNEL_PREFIX_COMMAND = "/add_channel "


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


def get_post_request_pattern(post_storage: PostStorage) -> re.Pattern:
    type_pattern = f"({'|'.join(t for t in (post_storage.get_all_custom_channel_types() + [ANY_CHANNEL_COMMAND]))})"
    amount_pattern = rf"(\d{{0,5}})"
    return re.compile(rf"/{type_pattern}{amount_pattern}")


async def create_bot(post_storage: PostStorage, warden: Warden) -> TelegramClient:
    logger.info("Creating bot")
    bot = TelegramClient(StringSession(BOT_SESSION), TELEGRAM_API_ID, TELEGRAM_API_HASH)

    @bot.on(events.NewMessage(pattern=get_post_request_pattern(post_storage), from_users=ADMIN))
    async def handle_posts_request_command(event) -> None:
        logger.info(f"Got {event.pattern_match} request")

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

    @bot.on(events.NewMessage(pattern=f"{ADD_CHANNEL_PREFIX_COMMAND}(.*)"))
    async def handle_adding_new_channel(event) -> None:
        logger.info(f"Got {event.pattern_match} request")

        try:
            channel_id = int(event.pattern_match.group(1).strip())
        except (TypeError, IndexError):
            raise ValueError(
                f"{event.pattern_match} doesn't satisfy the required structure: '{ADD_CHANNEL_PREFIX_COMMAND}<integer>'"
            )
        channel_name = get_display_name(channel_id)

        post_storage.add_channel(channel_id, channel_name)
        logger.info("Channel id={}, name={} has been added", channel_id, channel_name or "HIDDEN")
        await event.reply(
            f"Channel with id={channel_id}, name={channel_name or 'HIDDEN'} has been added."
            f" It's needed to wait up to {UPDATE_WHITELISTED_CHANNELS_INTERVAL} to refresh listening channels"
        )

    await bot.start()
    logger.info("Bot has been initialized")
    return bot
