"""Unit tests for ForwardService."""

from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock

import pytest

from app.exceptions import ForwardError
from schemas.forward import ForwardJob
from service.forward import ForwardService


@pytest.mark.asyncio
async def test_forward_message_calls_pyrogram_forward(monkeypatch) -> None:
    """Ensure forward_messages is called with same chat source and destination."""
    client = MagicMock()
    client.forward_messages = AsyncMock(return_value=None)
    holder = SimpleNamespace(client=client)
    monkeypatch.setattr(
        "service.forward.pyrogram_client",
        holder,
    )

    service = ForwardService()
    job = ForwardJob(chat_id=-1004215169273, message_id=5, index=0, total=1)
    await service.forward_message(job)

    client.forward_messages.assert_awaited_once_with(
        chat_id=-1004215169273,
        from_chat_id=-1004215169273,
        message_ids=5,
    )


@pytest.mark.asyncio
async def test_forward_message_wraps_errors(monkeypatch) -> None:
    """Ensure Telegram failures become ForwardError."""
    client = MagicMock()
    client.forward_messages = AsyncMock(side_effect=RuntimeError("boom"))
    holder = SimpleNamespace(client=client)
    monkeypatch.setattr(
        "service.forward.pyrogram_client",
        holder,
    )

    service = ForwardService()
    job = ForwardJob(chat_id=-1004215169273, message_id=5, index=0, total=1)
    with pytest.raises(ForwardError):
        await service.forward_message(job)


@pytest.mark.asyncio
async def test_run_daily_sequence_sleeps_between_messages(monkeypatch) -> None:
    """Ensure the service sleeps between messages but not after the last one."""
    service = ForwardService()
    calls: list[int] = []

    async def fake_forward(job) -> None:
        calls.append(job.message_id)

    sleeps: list[float] = []

    async def fake_sleep(seconds: float) -> None:
        sleeps.append(seconds)

    monkeypatch.setattr(service, "forward_message", fake_forward)
    monkeypatch.setattr(
        "service.forward.settings",
        SimpleNamespace(
            chat_id=-1004215169273,
            message_ids=[5, 7, 8],
            delay_hours=4.0,
        ),
    )
    monkeypatch.setattr("service.forward.asyncio.sleep", fake_sleep)

    await service.run_daily_sequence()

    assert calls == [5, 7, 8]
    assert sleeps == [4.0 * 3600, 4.0 * 3600]
