"""Entry point for the Telegram forwarder."""

import asyncio
from pathlib import Path

from app.config import settings
from app.integrations.mongo import find_mongo
from app.integrations.pyrogram_client import pyrogram_client
from logger.loguru import logger
from service import forward_service


async def run() -> None:
    """Connect Mongo and Telegram, then run the schedule loop forever."""
    await find_mongo.connect()
    await pyrogram_client.start()
    try:
        await forward_service.run_loop()
    finally:
        await pyrogram_client.stop()
        await find_mongo.close()


def main() -> None:
    """Run the async forwarder event loop."""
    Path(settings.workdir).mkdir(parents=True, exist_ok=True)
    logger.info("LunarisCasino forwarder starting")
    asyncio.run(run())


if __name__ == "__main__":
    main()
