# 5verst_bot

Telegram-бот для команды `5 вёрст`: генерация постов, шаблоны публикаций, адаптация текста под VK и базовая статистика использования.

## Стек

- Python 3.11+
- aiogram 3
- FastAPI + Uvicorn (webhook)
- OpenAI API

## Быстрый старт (локально)

1. Создать виртуальное окружение и установить зависимости:
```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

2. Скопировать `.env.example` в `.env` и заполнить значения.

3. Запустить:
```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

Проверка:
- `GET /health` -> статус приложения.
- webhook endpoint по умолчанию: `/webhook/telegram`.

## Переменные окружения

- `ENV`: `dev` или `prod`
- `DEV_BOT_TOKEN`: токен dev-бота (используется, когда `ENV=dev`)
- `BOT_TOKEN`: токен прод-бота (используется, когда `ENV=prod`)
- `OPENAI_API_KEY`: ключ OpenAI
- `OPENAI_MODEL`: модель OpenAI, по умолчанию `gpt-4o-mini`
- `WEBHOOK_HOST`: публичный URL приложения
- `WEBHOOK_PATH`: путь webhook, по умолчанию `/webhook/telegram`
- `WEBHOOK_SECRET`: секрет для webhook
- `ADMIN_ID`: Telegram ID администратора для `/users_stats`

## Деплой на Railway

В проекте добавлены:
- `Procfile`
- `railway.json`
- endpoint здоровья `/health`

Шаги:
1. Подключить репозиторий в Railway.
2. Задать переменные окружения из `.env.example`.
3. Убедиться, что `ENV=prod` и заполнен `BOT_TOKEN`.
4. После деплоя выставить `WEBHOOK_HOST` равным Railway-домену сервиса.

## Что важно перед push

- `.env` не должен попадать в git (уже добавлен в `.gitignore`).
- В репозитории не хранить runtime-файлы статистики и пользовательских настроек.
