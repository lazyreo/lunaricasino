"""Pydantic schemas for forwarding jobs."""

from pydantic import BaseModel, Field


class ForwardJob(BaseModel):
    """Describes a single forward of one source message."""

    chat_id: int = Field(description="Source and destination chat ID")
    message_id: int = Field(description="Telegram message ID to forward")
    index: int = Field(description="Zero-based position in the daily sequence")
    total: int = Field(description="Total messages in the daily sequence")
