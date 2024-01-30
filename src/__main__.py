from loguru import logger
from telethon import TelegramClient

from src.config import TELEGRAM_API_HASH, TELEGRAM_API_ID, TELEGRAM_BOT_TOKEN
from src.handlers import aggregator_channel_listener, handle_next_command, public_channel_listener

if __name__ == "__main__":
    client = TelegramClient("ChannelParser", TELEGRAM_API_ID, TELEGRAM_API_HASH)
    logger.info("Client has been initialized")
    bot = TelegramClient("bot", TELEGRAM_API_ID, TELEGRAM_API_HASH).start(bot_token=TELEGRAM_BOT_TOKEN)
    logger.info("Bot has been initialized")

    client.add_event_handler(public_channel_listener)
    bot.add_event_handler(aggregator_channel_listener)
    bot.add_event_handler(handle_next_command)

    client.start()
    bot.run_until_disconnected()
