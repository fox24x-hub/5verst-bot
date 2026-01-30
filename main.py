import logging
import os

from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import Update
from dotenv import load_dotenv
from fastapi import FastAPI, Request

from handlers import assistant_router, content_router

load_dotenv()
logging.basicConfig(level=logging.INFO)

ENV = os.getenv("ENV", "dev")  # "dev" или "prod"

if ENV == "prod":
    API_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
else:
    API_TOKEN = os.getenv("DEV_TELEGRAM_BOT_TOKEN")

WEBHOOK_URL = os.getenv("WEBHOOK_URL", "http://localhost:8000")
WEBHOOK_PATH = "/webhook/telegram"
WEBHOOK_SECRET = os.getenv("WEBHOOK_SECRET", "your-secret-key")

app = FastAPI()
bot = Bot(token=API_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(storage=storage)

dp.include_router(assistant_router)
dp.include_router(content_router)


@app.post(WEBHOOK_PATH)
async def webhook_handler(request: Request):
    """Handle incoming updates from Telegram via webhook"""
    try:
        data = await request.json()
        update = Update(**data)  # важно: создаём объект Update
        await dp.feed_update(bot, update)  # сюда уже идёт Update, а не dict
        return {"ok": True}
    except Exception as e:
        logging.exception(f"Webhook error: {e}")
        return {"ok": False, "error": str(e)}


@app.on_event("startup")
async def on_startup():
    """Register webhook on startup (логируем, а выставляешь вебхук через BotFather/скрипт)"""
    print(f"ENV = {ENV}")
    print(f"API_TOKEN = {API_TOKEN}")
    if not API_TOKEN:
        raise RuntimeError(
            "TELEGRAM_BOT_TOKEN / DEV_TELEGRAM_BOT_TOKEN не задан в .env"
        )

    logging.info(f"Бот запущен (webhook), ENV={ENV}")
    logging.info(f"Webhook URL (ожидаемый): {WEBHOOK_URL}{WEBHOOK_PATH}")


@app.on_event("shutdown")
async def on_shutdown():
    """Cleanup on shutdown"""
    await bot.session.close()


@app.get("/health")
async def health_check():
    """Health check endpoint for Railway"""
    return {"status": "healthy", "env": ENV}


if __name__ == "__main__":
    import uvicorn

    port = int(os.getenv("PORT", "8000"))
    uvicorn.run(app, host="0.0.0.0", port=port)
