"""Application settings loaded from environment variables."""

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Runtime configuration for the Telegram forwarder."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    api_id: int = Field(description="Telegram API ID from my.telegram.org")
    api_hash: str = Field(description="Telegram API hash from my.telegram.org")
    bot_token: str = Field(description="Bot token from @BotFather")
    session_name: str = Field(
        default="lunariscasino",
        description="Pyrogram session file name (without extension)",
    )
    chat_id: int = Field(
        default=-1004215169273,
        description="Source and destination chat/channel ID",
    )
    message_ids: list[int] = Field(
        default_factory=lambda: [5, 7, 8, 9, 10, 12, 13, 14, 15],
        description="Message IDs to forward in order, as-is",
    )
    delay_hours: float = Field(
        default=4.0,
        description="Hours to wait between consecutive message forwards",
    )
    workdir: str = Field(
        default="data",
        description="Directory for Pyrogram session files",
    )


settings = Settings()
