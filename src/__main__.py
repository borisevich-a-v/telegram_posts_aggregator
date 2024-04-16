from loguru import logger

from bot.craete_bot import create_bot
from bot.posts_storage import PostQueue
from bot.warden.warden import Warden
from telegram_agent.create_agent import create_telegram_agent
from telegram_agent.registered_messages import MessagesRegister

if __name__ == "__main__":
    logger.info("Starting application...")

    agent = create_telegram_agent(MessagesRegister())
    bot = create_bot(PostQueue(), Warden())

    # run the infinite loop
    agent.run_until_disconnected()
