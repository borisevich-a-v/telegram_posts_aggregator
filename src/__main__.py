from loguru import logger

from src.craete_bot import create_bot
from src.create_client import create_client
from src.posts_storage import PostQueue
from src.registered_messages import MessagesRegister
from src.warden.warden import Warden

if __name__ == "__main__":
    logger.info("Starting application...")

    client = create_client(MessagesRegister())
    bot = create_bot(PostQueue(), Warden())

    # run the infinite loop
    client.run_until_disconnected()
