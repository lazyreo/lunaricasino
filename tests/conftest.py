"""Shared pytest fixtures and environment defaults."""

import os

os.environ.setdefault("API_ID", "12345678")
os.environ.setdefault("API_HASH", "test_api_hash")
os.environ.setdefault("BOT_TOKEN", "123456789:AAHtest_bot_token")
