"""Pydantic schema for the forward schedule document."""

from datetime import datetime

from pydantic import BaseModel, Field


class ForwardSchedule(BaseModel):
    """Tracks which message is next and when it should be copied."""

    chat_id: int = Field(description="Telegram chat the schedule belongs to")
    next_index: int = Field(description="Zero-based index into configured message_ids")
    next_message_id: int = Field(description="Telegram message ID to copy next")
    next_at: datetime = Field(description="UTC time when the next copy should run")
    updated_at: datetime = Field(description="UTC time of the last schedule update")
