from loguru import logger
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from aggregator.bot.create_bot import create_bot
from aggregator.bot.warden.warden import Warden
from aggregator.config import DB_CONNECTION_STRING
from aggregator.posts_storage import PostStorage
from aggregator.telegram_agent.create_agent import create_telegram_agent

if __name__ == "__main__":
    logger.info("Starting application...")

    post_storage = PostStorage(sessionmaker(bind=create_engine(DB_CONNECTION_STRING)))
    tg_agent = create_telegram_agent(post_storage)
    bot = create_bot(post_storage, Warden())

    # run the infinite loop
    logger.info("The infinite loop is running")
    bot.run_until_disconnected()
