# Настройка и использование бота 5verst

## Обзор изменений

В проект добавлены следующие модули для автоматической генерации постов через ChatGPT:

### 1. **services/prompts.py**
Содержит:
- `FIVE_VERST_CONTENT_SYSTEM_PROMPT` — полный system-промпт, описывающий роль бота, стиль, ограничения и фокус контента
- `POST_STRUCTURE` — обязательная структура постов (заголовок, основной текст, призыв к действию, хештеги)

### 2. **services/knowledge.py**
Загружает справочные материалы из папки `data/`:
- `5-verst.txt` — основная информация о движении «5 вёрст»
- `posts_examples_structured.md` — структурированные примеры постов
- `posts_examples.md` — дополнительные примеры

Все файлы читаются один раз при импорте модуля.

### 3. **services/content_generator.py**
Функция `generate_post(topic, location)` генерирует посты:
- Использует `FIVE_VERST_CONTENT_SYSTEM_PROMPT` как system-роль
- Подмешивает знания из `knowledge.py` в user-промпт
- Отправляет запрос в OpenAI API
- Возвращает готовый текст поста

---

## Установка и настройка

### Шаг 1: Добавить файлы знаний в `data/`

Создай файлы:
```
data/
  5-verst.txt                       # Основная информация о движении
  posts_examples_structured.md       # Структурированные примеры постов
  posts_examples.md                  # Дополнительные примеры
```

Например, в `data/5-verst.txt`:
```
5 вёрст — это бесплатные еженедельные мероприятия на 5 км, проводимые силами волонтёров.
Это НЕ соревнование и не тренировка, а дружеские субботние встречи...
```

### Шаг 2: Настроить OpenAI API

В файле `.env` добавь:
```
OPENAI_API_KEY=sk-...
```

Проверь, что `services/openai_client.py` правильно инициализирует клиент.

### Шаг 3: Использовать в хэндлерах

Пример в `handlers/posts.py`:
```python
from aiogram import Router, F
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from services.content_generator import generate_post

router = Router()

class PostStates(StatesGroup):
    waiting_for_topic = State()

@router.message(F.text == "/new_post")
async def cmd_new_post(message: Message, state: FSMContext):
    await message.answer("О какой теме написать пост? Например: 'анонс субботней встречи', 'благодарность волонтёрам'.")
    await state.set_state(PostStates.waiting_for_topic)

@router.message(PostStates.waiting_for_topic)
async def process_topic(message: Message, state: FSMContext):
    topic = message.text
    await message.answer("Генерирую пост, подожди несколько секунд…")
    
    post_text = await generate_post(topic=topic, location="Екатеринбург")
    
    await message.answer(post_text, parse_mode=None)
    await state.clear()
```

Подключи роутер в `main.py`:
```python
from handlers import posts

dp.include_router(posts.router)
```

---

## Настройка Railway для Webhooks

### Вариант 1: FastAPI + aiogram

#### 1. Обнови `main.py`:
```python
import os
from fastapi import FastAPI, Request
from aiogram import Bot, Dispatcher
from aiogram.types import Update

BOT_TOKEN = os.getenv("BOT_TOKEN")
WEBHOOK_PATH = f"/webhook/{BOT_TOKEN}"
WEBHOOK_URL = os.getenv("WEBHOOK_URL")  # https://your-project.up.railway.app/webhook/...

bot = Bot(BOT_TOKEN)
dp = Dispatcher()

# Подключи роутеры:
from handlers import posts
dp.include_router(posts.router)

app = FastAPI()

@app.on_event("startup")
async def on_startup():
    await bot.set_webhook(WEBHOOK_URL)

@app.on_event("shutdown")
async def on_shutdown():
    await bot.delete_webhook()
    await bot.session.close()

@app.post(WEBHOOK_PATH)
async def telegram_webhook(request: Request):
    data = await request.json()
    update = Update.model_validate(data)
    await dp.feed_update(bot, update)
    return {"ok": True}
```

#### 2. Создай `Procfile` (если нужно):
```
web: uvicorn main:app --host 0.0.0.0 --port $PORT
```

#### 3. Настрой переменные окружения в Railway:
```
BOT_TOKEN=<твой токен>
WEBHOOK_URL=https://<твой проект>.up.railway.app/webhook/<BOT_TOKEN>
OPENAI_API_KEY=sk-...
```

#### 4. Деплой:
Railway автоматически развернёт проект после пуша в GitHub.

---

## Как работает генерация постов

1. Пользователь вызывает `/new_post`
2. Бот спрашивает тему
3. Пользователь вводит тему (например, «анонс»)
4. Бот вызывает `generate_post(topic="анонс", location="Екатеринбург")`:
   - Загружает `FIVE_VERST_KNOWLEDGE`, `POSTS_STRUCTURED_EXAMPLES` и `POST_STRUCTURE`
   - Формирует user-промпт с примерами и структурой
   - Отправляет запрос в OpenAI с system-промптом `FIVE_VERST_CONTENT_SYSTEM_PROMPT`
   - Получает готовый текст поста
5. Бот отправляет пост пользователю

---

## Доработка и расширение

### Добавить выбор локации
Можно сделать FSM с двумя шагами:
```python
class PostStates(StatesGroup):
    waiting_for_topic = State()
    waiting_for_location = State()

@router.message(PostStates.waiting_for_topic)
async def process_topic(message: Message, state: FSMContext):
    await state.update_data(topic=message.text)
    await message.answer("Укажи локацию (или пропусти, написав 'пропустить'):")
    await state.set_state(PostStates.waiting_for_location)

@router.message(PostStates.waiting_for_location)
async def process_location(message: Message, state: FSMContext):
    data = await state.get_data()
    topic = data["topic"]
    location = None if message.text.lower() == "пропустить" else message.text
    
    post_text = await generate_post(topic=topic, location=location)
    await message.answer(post_text)
    await state.clear()
```

### Настроить другие модели
В `content_generator.py` можно изменить:
```python
model="gpt-4o-mini",  # или "gpt-4", "gpt-3.5-turbo"
```

### Логирование и кэширование
Можно добавить сохранение сгенерированных постов в БД или файл для последующего анализа.

---

## Полезные ссылки

- [aiogram 3.x документация](https://docs.aiogram.dev/)
- [FastAPI документация](https://fastapi.tiangolo.com/)
- [Railway документация](https://docs.railway.app/)
- [OpenAI API документация](https://platform.openai.com/docs/)

---

Вопросы или проблемы? Открывай issue в репозитории!
