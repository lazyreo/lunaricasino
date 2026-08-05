"""Service that copies configured Telegram messages on a Mongo-backed schedule."""

import asyncio
from datetime import datetime, timezone

from app.config import settings
from app.exceptions import ForwardError
from app.integrations.pyrogram_client import pyrogram_client
from logger.loguru import logger
from repository.schedule import schedule_repository
from schemas.forward import ForwardJob
from schemas.schedule import ForwardSchedule


class ForwardService:
    """Copy a fixed message set, resuming from MongoDB schedule state."""

    async def forward_message(self, job: ForwardJob) -> None:
        """Copy one message into one destination chat without a forward tag."""
        client = pyrogram_client.client
        logger.bind(
            source_chat_id=job.source_chat_id,
            destination_chat_id=job.destination_chat_id,
            message_id=job.message_id,
            index=job.index,
            total=job.total,
        ).info("Copying message as-is without forward tag")
        try:
            await client.copy_message(
                chat_id=job.destination_chat_id,
                from_chat_id=job.source_chat_id,
                message_id=job.message_id,
            )
        except Exception as exc:
            logger.bind(
                source_chat_id=job.source_chat_id,
                destination_chat_id=job.destination_chat_id,
                message_id=job.message_id,
                error=str(exc),
            ).error("Failed to copy message")
            raise ForwardError(
                f"Failed to copy message {job.message_id} from "
                f"{job.source_chat_id} to {job.destination_chat_id}"
            ) from exc
        logger.bind(
            source_chat_id=job.source_chat_id,
            destination_chat_id=job.destination_chat_id,
            message_id=job.message_id,
            index=job.index,
            total=job.total,
        ).info("Message copied successfully")

    async def _sleep_until(self, next_at: datetime) -> None:
        """Sleep until the schedule due time when it is still in the future."""
        due_at = next_at
        if due_at.tzinfo is None:
            due_at = due_at.replace(tzinfo=timezone.utc)
        else:
            due_at = due_at.astimezone(timezone.utc)

        now = datetime.now(timezone.utc)
        delay_seconds = (due_at - now).total_seconds()
        if delay_seconds <= 0:
            logger.bind(next_at=due_at.isoformat()).info("Schedule is due; sending now")
            return

        logger.bind(
            sleep_seconds=delay_seconds,
            next_at=due_at.isoformat(),
        ).info("Waiting until next scheduled message")
        await asyncio.sleep(delay_seconds)

    async def process_next(self, schedule: ForwardSchedule) -> ForwardSchedule:
        """Wait for the due time, copy to all destinations, then advance schedule."""
        await self._sleep_until(schedule.next_at)
        total = len(settings.message_ids)
        for destination_chat_id in settings.destination_chat_ids:
            job = ForwardJob(
                source_chat_id=settings.chat_id,
                destination_chat_id=destination_chat_id,
                message_id=schedule.next_message_id,
                index=schedule.next_index,
                total=total,
            )
            await self.forward_message(job)
        return await schedule_repository.advance_after_send(schedule)

    async def run_loop(self) -> None:
        """Load Mongo schedule state and process messages forever."""
        logger.bind(
            source_chat_id=settings.chat_id,
            destination_chat_ids=settings.destination_chat_ids,
        ).info("Starting Mongo-backed forward loop")
        while True:
            schedule = await schedule_repository.get_or_create()
            await self.process_next(schedule)


forward_service = ForwardService()
