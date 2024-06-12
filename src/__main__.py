from loguru import logger
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from bot.create_bot import create_bot
from bot.posts_storage import PostStorage
from bot.warden.warden import Warden
from config import DB_CONNECTION_STRING
from telegram_agent.create_agent import create_telegram_agent
from telegram_agent.registered_messages import MessagesRegister

if __name__ == "__main__":
    logger.info("Starting application...")

    session_maker = sessionmaker(bind=create_engine(DB_CONNECTION_STRING))

    tg_agent = create_telegram_agent(MessagesRegister())
    bot = create_bot(PostStorage(session_maker), Warden())

    # run the infinite loop
    logger.info("The infinite loop is running")
    bot.run_until_disconnected()
