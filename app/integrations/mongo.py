"""Lightweight Motor async MongoDB client wrapper."""

from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorCollection, AsyncIOMotorDatabase

from app.config import settings
from app.exceptions import MongoNotConnectedError
from logger.loguru import logger


class FindMongo:
    """Singleton async Mongo helper built on Motor."""

    def __init__(self) -> None:
        """Initialize an unconnected Mongo client holder."""
        self._client: AsyncIOMotorClient | None = None
        self._db: AsyncIOMotorDatabase | None = None

    async def connect(self) -> None:
        """Connect to MongoDB and ping the server."""
        self._client = AsyncIOMotorClient(settings.mongo_uri)
        self._db = self._client[settings.mongo_db]
        await self._client.admin.command("ping")
        logger.bind(mongo_db=settings.mongo_db).info("FindMongo connected")

    async def close(self) -> None:
        """Close the MongoDB client when connected."""
        if self._client is None:
            return
        self._client.close()
        self._client = None
        self._db = None
        logger.info("FindMongo closed")

    @property
    def db(self) -> AsyncIOMotorDatabase:
        """Return the active database or raise if not connected."""
        if self._db is None:
            raise MongoNotConnectedError("FindMongo has not been connected yet")
        return self._db

    def collection(self, name: str) -> AsyncIOMotorCollection:
        """Return a named collection from the active database."""
        return self.db[name]


find_mongo = FindMongo()
