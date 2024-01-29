from loguru import logger
from telethon import TelegramClient

from src.config import TELEGRAM_API_HASH, TELEGRAM_API_ID, TELEGRAM_BOT_TOKEN
from src.handlers import aggregator_channel_listener, handle_next_command, public_channel_listener

if __name__ == "__main__":
    logger.info("Initialization of client")

    client = TelegramClient("ChannelParser", TELEGRAM_API_ID, TELEGRAM_API_HASH)
    client.add_event_handler(public_channel_listener)

    logger.info("Client has been initialized")

    logger.info("initialization of bot")

    bot = TelegramClient("bot", TELEGRAM_API_ID, TELEGRAM_API_HASH).start(bot_token=TELEGRAM_BOT_TOKEN)
    bot.add_event_handler(aggregator_channel_listener)
    bot.add_event_handler(handle_next_command)

    logger.info("Bot has been initialized")

    client.start()
    bot.run_until_disconnected()
