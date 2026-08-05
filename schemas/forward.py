"""Pydantic schemas for forwarding jobs."""

from pydantic import BaseModel, Field


class ForwardJob(BaseModel):
    """Describes a single copy of one source message into a destination chat."""

    source_chat_id: int = Field(description="Chat ID that contains the original message")
    destination_chat_id: int = Field(description="Chat ID to copy the message into")
    message_id: int = Field(description="Telegram message ID to copy")
    index: int = Field(description="Zero-based position in the sequence")
    total: int = Field(description="Total messages in the sequence")
