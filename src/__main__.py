from loguru import logger

from craete_bot import create_bot
from create_client import create_client
from posts_storage import PostQueue
from registered_messages import MessagesRegister
from warden.warden import Warden

if __name__ == "__main__":
    logger.info("Starting application...")

    client = create_client(MessagesRegister())
    bot = create_bot(PostQueue(), Warden())

    # run the infinite loop
    client.run_until_disconnected()
