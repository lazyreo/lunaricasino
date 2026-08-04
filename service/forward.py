"""Service that forwards configured Telegram messages as-is."""

import asyncio

from app.config import settings
from app.exceptions import ForwardError
from app.integrations.pyrogram_client import pyrogram_client
from logger.loguru import logger
from schemas.forward import ForwardJob


class ForwardService:
    """Forward a fixed message set with a delay between each item."""

    async def forward_message(self, job: ForwardJob) -> None:
        """Forward one message into the same chat without rewriting content."""
        client = pyrogram_client.client
        logger.bind(
            chat_id=job.chat_id,
            message_id=job.message_id,
            index=job.index,
            total=job.total,
        ).info("Forwarding message as-is")
        try:
            await client.forward_messages(
                chat_id=job.chat_id,
                from_chat_id=job.chat_id,
                message_ids=job.message_id,
            )
        except Exception as exc:
            logger.bind(
                chat_id=job.chat_id,
                message_id=job.message_id,
                error=str(exc),
            ).error("Failed to forward message")
            raise ForwardError(
                f"Failed to forward message {job.message_id} in chat {job.chat_id}"
            ) from exc
        logger.bind(
            chat_id=job.chat_id,
            message_id=job.message_id,
            index=job.index,
            total=job.total,
        ).info("Message forwarded successfully")

    async def run_daily_sequence(self) -> None:
        """Forward all configured messages with the configured gap between each."""
        message_ids = list(settings.message_ids)
        total = len(message_ids)
        delay_seconds = settings.delay_hours * 3600
        logger.bind(
            chat_id=settings.chat_id,
            message_count=total,
            delay_hours=settings.delay_hours,
        ).info("Starting daily forward sequence")

        for index, message_id in enumerate(message_ids):
            job = ForwardJob(
                chat_id=settings.chat_id,
                message_id=message_id,
                index=index,
                total=total,
            )
            await self.forward_message(job)
            if index < total - 1:
                logger.bind(
                    sleep_hours=settings.delay_hours,
                    next_message_id=message_ids[index + 1],
                ).info("Waiting before next forward")
                await asyncio.sleep(delay_seconds)

        logger.bind(chat_id=settings.chat_id, message_count=total).info(
            "Daily forward sequence completed"
        )


forward_service = ForwardService()
