from telethon import TelegramClient
from telethon.sessions import StringSession

from src.config import TELEGRAM_API_HASH, TELEGRAM_API_ID

with TelegramClient(StringSession(), TELEGRAM_API_ID, TELEGRAM_API_HASH) as client:
    print(client.session.save())
