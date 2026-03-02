import logging

from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import Update
from fastapi import FastAPI, Request

from config import settings
from handlers import assistant_router, content_router

logging.basicConfig(level=logging.INFO)

if not settings.bot_token:
    raise RuntimeError("BOT_TOKEN / DEV_BOT_TOKEN не задан в .env")

app = FastAPI()
bot = Bot(token=settings.bot_token)
storage = MemoryStorage()
dp = Dispatcher(storage=storage)

dp.include_router(content_router)
dp.include_router(assistant_router)


@app.post(settings.webhook_path)
async def webhook_handler(request: Request):
    try:
        data = await request.json()
        logging.info(f"Incoming update: {data}")
        update = Update(**data)
        await dp.feed_update(bot, update)
        return {"ok": True}
    except Exception as e:
        logging.exception(f"Webhook error: {e}")
        return {"ok": False, "error": str(e)}


@app.on_event("startup")
async def on_startup():
    logging.info(f"Бот запущен (webhook), ENV={settings.env}")
    logging.info(f"Webhook ожидается на: {settings.webhook_host}{settings.webhook_path}")


@app.on_event("shutdown")
async def on_shutdown():
    await bot.session.close()


@app.get("/health")
async def health_check():
    return {"status": "healthy", "env": settings.env}
