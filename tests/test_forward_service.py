"""Unit tests for ForwardService."""

from datetime import datetime, timedelta, timezone
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock

import pytest

from app.exceptions import ForwardError
from schemas.forward import ForwardJob
from schemas.schedule import ForwardSchedule
from service.forward import ForwardService


@pytest.mark.asyncio
async def test_forward_message_calls_pyrogram_copy(monkeypatch) -> None:
    """Ensure copy_message copies from source chat into destination chat."""
    client = MagicMock()
    client.copy_message = AsyncMock(return_value=None)
    holder = SimpleNamespace(client=client)
    monkeypatch.setattr(
        "service.forward.pyrogram_client",
        holder,
    )

    service = ForwardService()
    job = ForwardJob(
        source_chat_id=-1004215169273,
        destination_chat_id=-1003690377297,
        message_id=5,
        index=0,
        total=1,
    )
    await service.forward_message(job)

    client.copy_message.assert_awaited_once_with(
        chat_id=-1003690377297,
        from_chat_id=-1004215169273,
        message_id=5,
    )


@pytest.mark.asyncio
async def test_forward_message_wraps_errors(monkeypatch) -> None:
    """Ensure Telegram failures become ForwardError."""
    client = MagicMock()
    client.copy_message = AsyncMock(side_effect=RuntimeError("boom"))
    holder = SimpleNamespace(client=client)
    monkeypatch.setattr(
        "service.forward.pyrogram_client",
        holder,
    )

    service = ForwardService()
    job = ForwardJob(
        source_chat_id=-1004215169273,
        destination_chat_id=-1003690377297,
        message_id=5,
        index=0,
        total=1,
    )
    with pytest.raises(ForwardError):
        await service.forward_message(job)


@pytest.mark.asyncio
async def test_sleep_until_waits_for_future_due_time(monkeypatch) -> None:
    """Ensure the service sleeps only when next_at is in the future."""
    service = ForwardService()
    sleeps: list[float] = []

    async def fake_sleep(seconds: float) -> None:
        sleeps.append(seconds)

    monkeypatch.setattr("service.forward.asyncio.sleep", fake_sleep)
    fixed_now = datetime(2026, 8, 4, 12, 0, tzinfo=timezone.utc)

    class FixedDateTime(datetime):
        @classmethod
        def now(cls, tz=None):
            return fixed_now if tz is not None else fixed_now.replace(tzinfo=None)

    monkeypatch.setattr("service.forward.datetime", FixedDateTime)

    due = fixed_now + timedelta(hours=2)
    await service._sleep_until(due)
    assert len(sleeps) == 1
    assert sleeps[0] == pytest.approx(2 * 3600)

    sleeps.clear()
    await service._sleep_until(fixed_now - timedelta(seconds=1))
    assert sleeps == []


@pytest.mark.asyncio
async def test_process_next_copies_to_all_destinations(monkeypatch) -> None:
    """Ensure process_next copies the due message to every destination chat."""
    service = ForwardService()
    forwarded: list[ForwardJob] = []

    async def fake_sleep_until(_next_at: datetime) -> None:
        return None

    async def fake_forward(job: ForwardJob) -> None:
        forwarded.append(job)

    advanced = ForwardSchedule(
        chat_id=-1004215169273,
        next_index=1,
        next_message_id=7,
        next_at=datetime(2026, 8, 4, 16, 0, tzinfo=timezone.utc),
        updated_at=datetime(2026, 8, 4, 12, 0, tzinfo=timezone.utc),
    )
    advance = AsyncMock(return_value=advanced)

    monkeypatch.setattr(service, "_sleep_until", fake_sleep_until)
    monkeypatch.setattr(service, "forward_message", fake_forward)
    monkeypatch.setattr("service.forward.schedule_repository.advance_after_send", advance)
    monkeypatch.setattr(
        "service.forward.settings",
        SimpleNamespace(
            message_ids=[5, 7, 8],
            chat_id=-1004215169273,
            destination_chat_ids=[-1004215169273, -1003690377297],
        ),
    )

    current = ForwardSchedule(
        chat_id=-1004215169273,
        next_index=0,
        next_message_id=5,
        next_at=datetime(2026, 8, 4, 12, 0, tzinfo=timezone.utc),
        updated_at=datetime(2026, 8, 4, 12, 0, tzinfo=timezone.utc),
    )
    result = await service.process_next(current)

    assert [job.destination_chat_id for job in forwarded] == [
        -1004215169273,
        -1003690377297,
    ]
    assert all(job.message_id == 5 for job in forwarded)
    assert all(job.source_chat_id == -1004215169273 for job in forwarded)
    advance.assert_awaited_once_with(current)
    assert result.next_message_id == 7
