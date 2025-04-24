import contextlib
from typing import AsyncIterator

from sqlalchemy.ext.asyncio import AsyncConnection, AsyncEngine, AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class DatabaseSessionManager:
    """Singleton"""

    _instance = None

    def __new__(cls, conn_string: str):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._conn_string = conn_string
        elif conn_string != cls._instance._conn_string:
            raise ValueError(
                f"Connection string cannot be changed (was: {cls._instance._conn_string}, tried: {conn_string})"
            )
        return cls._instance

    def __init__(self, conn_string: str):
        if getattr(self, "_initialized", False):
            return

        self._engine: AsyncEngine = create_async_engine(conn_string)
        self._sessionmaker: async_sessionmaker = async_sessionmaker(autocommit=False, bind=self._engine)
        self._initialized = True

    async def close(self) -> None:
        if self._engine is None:
            raise Exception("DatabaseSessionManager is not initialized")
        await self._engine.dispose()
        self._engine = None
        self._sessionmaker = None

    @contextlib.asynccontextmanager
    async def connect(self) -> AsyncIterator[AsyncConnection]:
        if self._engine is None:
            raise Exception("DatabaseSessionManager is not initialized")

        async with self._engine.begin() as connection:
            try:
                yield connection
            except Exception:
                await connection.rollback()
                raise

    @contextlib.asynccontextmanager
    async def session(self) -> AsyncIterator[AsyncSession]:
        if self._sessionmaker is None:
            raise Exception("DatabaseSessionManager is not initialized")

        session = self._sessionmaker()
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()
