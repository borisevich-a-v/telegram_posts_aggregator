import pytest
from unittest.mock import AsyncMock

import aggregator.db as db_module


class DummySessionManager:
    def __init__(self):
        self._default_session = AsyncMock(name="AsyncSessionMock")

    @pytest.fixture(autouse=True, scope="session")
    def _inject(self, monkeypatch):
        print("inside inject")
        monkeypatch.setattr(db_module, "sessionmanager", self)

    def session(self):
        print("inside session")

        async def _cm():
            try:
                yield self._default_session
            finally:
                pass

        return _cm()


_dummy_sm = DummySessionManager()
