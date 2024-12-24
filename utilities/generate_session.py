import sys

from telethon import TelegramClient
from telethon.sessions import StringSession

from aggregator.config import TELEGRAM_API_HASH, TELEGRAM_API_ID, TELEGRAM_BOT_TOKEN


def generate_client_session():
    print("Generating client session")
    with TelegramClient(StringSession(), TELEGRAM_API_ID, TELEGRAM_API_HASH) as client:
        print("Client session")
        print(client.session.save())


def generate_bot_session():
    print("Generating bot session")
    with TelegramClient(StringSession(), TELEGRAM_API_ID, TELEGRAM_API_HASH).start(bot_token=TELEGRAM_BOT_TOKEN) as bot:
        print("Bot session:")
        print(bot.sesson.save())


if len(sys.argv) != 2:
    raise ValueError(f"A single flag should be passed into {__file__}")

if sys.argv[1] == "--bot":
    generate_bot_session()
elif sys.argv[1] == "--client":
    generate_client_session()
else:
    raise ValueError("Unexpected flag")
