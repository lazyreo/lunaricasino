"""MongoDB repository for forward schedule state."""

from datetime import datetime, timedelta, timezone

from app.config import settings
from app.exceptions import ScheduleError
from app.integrations.mongo import find_mongo
from logger.loguru import logger
from schemas.schedule import ForwardSchedule

SCHEDULE_DOC_ID = "forward_schedule"


class ScheduleRepository:
    """Persist and load the next-message schedule via FindMongo."""

    def _collection(self):
        """Return the schedule collection."""
        return find_mongo.collection(settings.mongo_schedule_collection)

    async def get_or_create(self) -> ForwardSchedule:
        """Load the schedule, or create one that first runs after DELAY_HOURS."""
        collection = self._collection()
        document = await collection.find_one({"_id": SCHEDULE_DOC_ID})
        if document is not None:
            if document.get("next_at") is not None and document["next_at"].tzinfo is None:
                document["next_at"] = document["next_at"].replace(tzinfo=timezone.utc)
            if document.get("updated_at") is not None and document["updated_at"].tzinfo is None:
                document["updated_at"] = document["updated_at"].replace(tzinfo=timezone.utc)
            schedule = ForwardSchedule.model_validate(document)
            logger.bind(
                next_index=schedule.next_index,
                next_message_id=schedule.next_message_id,
                next_at=schedule.next_at.isoformat(),
            ).info("Loaded forward schedule from MongoDB")
            return schedule

        now = datetime.now(timezone.utc)
        message_ids = list(settings.message_ids)
        if not message_ids:
            raise ScheduleError("MESSAGE_IDS is empty; cannot create a schedule")

        # First boot: do not copy immediately; wait one full delay interval.
        schedule = ForwardSchedule(
            chat_id=settings.chat_id,
            next_index=0,
            next_message_id=message_ids[0],
            next_at=now + timedelta(hours=settings.delay_hours),
            updated_at=now,
        )
        await collection.insert_one({"_id": SCHEDULE_DOC_ID, **schedule.model_dump()})
        logger.bind(
            next_message_id=schedule.next_message_id,
            next_at=schedule.next_at.isoformat(),
            delay_hours=settings.delay_hours,
        ).info("Created first-run schedule; skipping immediate copy")
        return schedule

    async def advance_after_send(self, current: ForwardSchedule) -> ForwardSchedule:
        """Move to the next message and schedule it after the configured delay."""
        message_ids = list(settings.message_ids)
        if not message_ids:
            raise ScheduleError("MESSAGE_IDS is empty; cannot advance schedule")

        now = datetime.now(timezone.utc)
        next_index = (current.next_index + 1) % len(message_ids)
        schedule = ForwardSchedule(
            chat_id=settings.chat_id,
            next_index=next_index,
            next_message_id=message_ids[next_index],
            next_at=now + timedelta(hours=settings.delay_hours),
            updated_at=now,
        )
        result = await self._collection().update_one(
            {"_id": SCHEDULE_DOC_ID},
            {"$set": schedule.model_dump()},
            upsert=True,
        )
        if result.matched_count == 0 and result.upserted_id is None:
            raise ScheduleError("Failed to persist advanced forward schedule")

        logger.bind(
            next_index=schedule.next_index,
            next_message_id=schedule.next_message_id,
            next_at=schedule.next_at.isoformat(),
        ).info("Advanced forward schedule in MongoDB")
        return schedule


schedule_repository = ScheduleRepository()
