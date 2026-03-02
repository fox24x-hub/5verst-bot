import os
from dataclasses import dataclass

from dotenv import load_dotenv

load_dotenv()


def _int_env(name: str, default: int) -> int:
    value = os.getenv(name)
    if value is None:
        return default
    try:
        return int(value)
    except ValueError:
        return default


@dataclass(frozen=True)
class Settings:
    env: str
    bot_token: str | None
    webhook_host: str
    webhook_path: str
    webhook_secret: str
    openai_api_key: str | None
    openai_model: str
    admin_id: int


def _build_settings() -> Settings:
    env = os.getenv("ENV", "dev").strip().lower()
    bot_token = os.getenv("BOT_TOKEN") if env == "prod" else os.getenv("DEV_BOT_TOKEN")

    return Settings(
        env=env,
        bot_token=bot_token,
        webhook_host=os.getenv("WEBHOOK_HOST", "http://localhost:8000"),
        webhook_path=os.getenv("WEBHOOK_PATH", "/webhook/telegram"),
        webhook_secret=os.getenv("WEBHOOK_SECRET", "your-secret-key"),
        openai_api_key=os.getenv("OPENAI_API_KEY"),
        openai_model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
        admin_id=_int_env("ADMIN_ID", 106041882),
    )


settings = _build_settings()
