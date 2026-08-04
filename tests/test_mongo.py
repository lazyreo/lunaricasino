"""Unit tests for FindMongo wrapper."""

from unittest.mock import AsyncMock, MagicMock

import pytest

from app.exceptions import MongoNotConnectedError
from app.integrations.mongo import FindMongo


@pytest.mark.asyncio
async def test_collection_requires_connect() -> None:
    """Ensure collection access fails before connect."""
    mongo = FindMongo()
    with pytest.raises(MongoNotConnectedError):
        mongo.collection("forward_schedule")


@pytest.mark.asyncio
async def test_connect_pings_and_sets_db(monkeypatch) -> None:
    """Ensure connect stores client/db after a successful ping."""
    mongo = FindMongo()
    fake_client = MagicMock()
    fake_client.admin.command = AsyncMock(return_value={"ok": 1})
    fake_db = object()
    fake_client.__getitem__.return_value = fake_db

    monkeypatch.setattr(
        "app.integrations.mongo.AsyncIOMotorClient",
        MagicMock(return_value=fake_client),
    )
    monkeypatch.setattr(
        "app.integrations.mongo.settings",
        MagicMock(mongo_uri="mongodb://localhost:27017", mongo_db="lunariscasino"),
    )

    await mongo.connect()

    assert mongo.db is fake_db
    fake_client.admin.command.assert_awaited_once_with("ping")

    await mongo.close()
    fake_client.close.assert_called_once()
