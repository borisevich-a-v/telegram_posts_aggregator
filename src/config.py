import os

from dotenv import load_dotenv

load_dotenv()

LIST_DELIMITER = "|"


def load_env_list(env_name: str) -> list[str]:
    return os.environ[env_name].split(LIST_DELIMITER)


TELEGRAM_BOT_TOKEN = str(os.environ["TELEGRAM_BOT_TOKEN"])
TELEGRAM_API_ID = str(os.environ["TELEGRAM_API_ID"])
TELEGRAM_API_HASH = str(os.environ["TELEGRAM_API_HASH"])

ADMIN = str(os.environ["ADMIN"])

FUN_CHANNELS = load_env_list("FUN_CHANNELS")
NEWS_CHANNELS = load_env_list("NEWS_CHANNELS")

AGGREGATOR_CHANNEL = str(os.environ["AGGREGATOR_CHANNEL"])
