import asyncio

from loguru import logger

from aggregator import config
from aggregator.bot.create_bot import create_bot
from aggregator.bot.warden.warden import Warden
from aggregator.db import DatabaseSessionManager
from aggregator.openai_driver import OpenaiDriver
from aggregator.posts_storage import PostStorage
from aggregator.telegram_agent.create_agent import create_telegram_agent

if __name__ == "__main__":
    logger.info("Starting application...")
    post_storage = PostStorage(DatabaseSessionManager(config.DB_CONNECTION_STRING))
    openai_driver = OpenaiDriver(config)
    event_loop = asyncio.new_event_loop()

    telegram_agent_task = event_loop.create_task(create_telegram_agent(post_storage, openai_driver))
    bot_task = event_loop.create_task(create_bot(post_storage, Warden(), openai_driver))

    logger.info("The infinite loop is running")
    event_loop.run_forever()
