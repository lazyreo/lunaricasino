"""Entry point for the Telegram forwarder."""

import asyncio
from pathlib import Path

from app.config import settings
from app.integrations.pyrogram_client import pyrogram_client
from logger.loguru import logger
from service import forward_service


async def run() -> None:
    """Start Telegram and run forward cycles forever with no rest between cycles."""
    await pyrogram_client.start()
    try:
        while True:
            logger.info("Beginning new forward cycle")
            await forward_service.run_daily_sequence()
    finally:
        await pyrogram_client.stop()


def main() -> None:
    """Run the async forwarder event loop."""
    Path(settings.workdir).mkdir(parents=True, exist_ok=True)
    logger.info("LunarisCasino forwarder starting")
    asyncio.run(run())


if __name__ == "__main__":
    main()
