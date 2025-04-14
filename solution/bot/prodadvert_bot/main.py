import os
import asyncio
import logging
import shutil
import sys

from dishka import make_async_container
from dishka.integrations.aiogram import setup_dishka

from prodadvert_bot.bot import AppBot
from prodadvert_bot.config import Config
from prodadvert_bot.di import AppProvider

logging.basicConfig(level=logging.INFO, stream=sys.stdout)

config = Config()
container = make_async_container(
    AppProvider(),
    context={
        Config: config,
    }
)


async def main() -> None:
    """Entrypoint."""
    token = os.getenv("BOT_TOKEN")
    if os.path.exists("plots"):
        shutil.rmtree("plots")
    if not token:
        raise ValueError("No token available in current env")
    bot = AppBot(token)
    setup_dishka(container=container, router=bot.dispatcher)
    await bot.run()


if __name__ == '__main__':
    asyncio.run(main())
