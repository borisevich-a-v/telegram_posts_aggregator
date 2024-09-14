import os

import pendulum
from dotenv import load_dotenv
from loguru import logger

if os.environ.get("ENVIRONMENT") == "container":
    logger.info("Starting in a container")
    dot_env_found = load_dotenv(".env")
else:
    logger.info("Starting locally")
    dot_env_found = load_dotenv(".env_local") or load_dotenv("../.env_local")

if not dot_env_found:
    raise FileNotFoundError("There is no .env file")


LIST_DELIMITER = "|"


def load_env_list(env_name: str) -> list[str]:
    return os.environ.get(env_name, "").split(LIST_DELIMITER)


TELEGRAM_BOT_TOKEN = str(os.environ.get("TELEGRAM_BOT_TOKEN"))
TELEGRAM_API_ID = str(os.environ.get("TELEGRAM_API_ID"))
TELEGRAM_API_HASH = str(os.environ.get("TELEGRAM_API_HASH"))

CLIENT_SESSION = str(os.environ.get("CLIENT_SESSION"))
DB_CONNECTION_STRING = str(os.environ.get("DB_CONNECTION_STRING"))

ADMIN = int(os.environ.get("ADMIN", 0))

FUN_CHANNELS = load_env_list("FUN_CHANNELS")
NEWS_CHANNELS = load_env_list("NEWS_CHANNELS")

AGGREGATOR_CHANNEL = str(os.environ.get("AGGREGATOR_CHANNEL"))

USER_TIME_ZONE = pendulum.timezone(str(os.environ.get("TIMEZONE", "UTC")))  # The developer is the only user
