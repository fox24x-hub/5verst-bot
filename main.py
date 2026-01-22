# main.py
import asyncio
import logging
import os

from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from dotenv import load_dotenv

from handlers import assistant_router, content_router


load_dotenv()
logging.basicConfig(level=logging.INFO)

ENV = os.getenv("ENV", "dev")  # "dev" или "prod"

if ENV == "prod":
    API_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
else:
    API_TOKEN = os.getenv("DEV_TELEGRAM_BOT_TOKEN")


async def main():
    print("ENV =", ENV)
    print("API_TOKEN =", API_TOKEN)

    bot = Bot(token=API_TOKEN)
    storage = MemoryStorage()
    dp = Dispatcher(storage=storage)

    dp.include_router(assistant_router)
    dp.include_router(content_router)

    logging.info(f"Бот запущен (long polling), ENV={ENV}")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
