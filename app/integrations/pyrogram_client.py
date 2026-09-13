"""Pyrogram Telegram client integration."""

from pyrogram.client import Client

from app.config import settings
from app.exceptions import ClientNotStartedError
from logger.loguru import logger


class PyrogramClient:
    """Singleton wrapper around a Pyrogram bot client."""

    def __init__(self) -> None:
        """Initialize an unstarted client holder."""
        self._client = None

    def build(self):
        """Create and store a configured Pyrogram bot client."""
        self._client = Client(
            name=settings.session_name,
            api_id=settings.api_id,
            api_hash=settings.api_hash,
            bot_token=settings.bot_token,
            workdir=settings.workdir,
            in_memory=True,
        )
        logger.bind(session_name=settings.session_name).info("Pyrogram bot client built")
        return self._client

    @property
    def client(self):
        """Return the active Pyrogram client or raise if missing."""
        if self._client is None:
            raise ClientNotStartedError("Pyrogram client has not been built yet")
        return self._client

    async def start(self) -> None:
        """Start the underlying Pyrogram bot client."""
        if self._client is None:
            self.build()
        await self._client.start()
        me = await self._client.get_me()
        logger.bind(user_id=me.id, username=me.username).info("Pyrogram bot client started")

    async def stop(self) -> None:
        """Stop the underlying Pyrogram client when running."""
        if self._client is None:
            return
        if self._client.is_connected:
            await self._client.stop()
            logger.info("Pyrogram bot client stopped")


pyrogram_client = PyrogramClient()
