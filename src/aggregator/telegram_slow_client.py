import asyncio
import time
from typing import Any

from loguru import logger
from telethon import TelegramClient


class TelegramSlowClient(TelegramClient):
    """Intend to guarantee minimum interval between some requests to telegram server."""

    _METHODS_WITH_PAUSE = {"forward_messages", "reply"}

    def __init__(self, *args, min_request_interval, **kwargs):
        self._min_request_interval = min_request_interval
        super().__init__(*args, *kwargs)

    def __getattribute__(self, name: str) -> Any:
        if name in ("_METHODS_WITH_PAUSE", "_min_request_interval"):
            return object.__getattribute__(self, name)

        original_attr = object.__getattribute__(self, name)

        if name in self._METHODS_WITH_PAUSE:

            if asyncio.iscoroutinefunction(original_attr):

                async def wrapped(*args, **kwargs):
                    result = await original_attr(*args, **kwargs)
                    time.sleep(self._min_request_interval)
                    return result

            else:

                def wrapped(*args, **kwargs):
                    logger.info("Real invoke meth")
                    result = original_attr(*args, **kwargs)
                    logger.info("Start sleep")
                    time.sleep(self._min_request_interval)
                    logger.info("Finish sleep")
                    return result

            return wrapped
        return original_attr
