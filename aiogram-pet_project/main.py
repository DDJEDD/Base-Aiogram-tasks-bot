import asyncio
import logging
import sys
import os
from dotenv import load_dotenv
from aiogram import Bot, Dispatcher, html
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from app.tasks import tasks
from app.menu import menu

load_dotenv()
TOKEN = os.getenv("BOT_TOKEN")


async def main() -> None:
    manager = Dispatcher()
    manager.include_router(menu)
    manager.include_router(tasks)
    bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    await manager.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())