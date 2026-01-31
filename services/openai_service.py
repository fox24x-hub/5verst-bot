import os
from dotenv import load_dotenv
from openai import AsyncOpenAI

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
print("OPENAI_API_KEY in openai_service:", (OPENAI_API_KEY or "")[:8])

OPENAI_MODEL = "gpt-4o-mini"

client = AsyncOpenAI(api_key=OPENAI_API_KEY)

# Константы для пятничного напоминания
FRIDAY_TIMING_TEMPLATE = (
    "Напоминаем наше расписание:\n\n"
    "08:30 — сбор и инструктаж волонтёров\n"
    "08:40 — сбор участников\n"
    "08:45 — разминка\n"
    "08:50 — инструктаж новых участников у стелы\n"
    "08:55 — общий брифинг\n"
    "09:00 — старт."
)

FRIDAY_LINKS_TEMPLATE = (
    "Как найти нас в парке: https://5verst.ru/parkmayakovskogo/course/\n\n"
    "Регистрация для тех, кто у нас первый раз: https://5verst.ru/register/"
)

REAL_POST_EXAMPLES = """
... твой длинный текст примеров ...
"""

SYSTEM_PROMPT = f"""... как у тебя ...""".strip()


async def _call_openai(
    user_content: str,
    max_tokens: int = 600,
    temperature: float = 0.85,
) -> str:
    if not OPENAI_API_KEY:
        return (
            "[ТЕСТОВЫЙ РЕЖИМ БЕЗ OPENAI]\n\n"
            "OPENAI_API_KEY не найден. Проверь файл .env и перезапусти бота."
        )

    response = await client.chat.completions.create(
        model=OPENAI_MODEL,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_content},
        ],
        temperature=temperature,
        max_tokens=max_tokens,
    )
    return response.choices[0].message.content.strip()


async def generate_post(
    topic: str,
    post_type: str = "announcement",
    platform: str = "telegram",
) -> str:
    type_map = {
        "volunteer_call": "пост-набор волонтёров",
        "event_announcement": "анонс субботнего мероприятия или праздника",
        "event_report": "короткий отчёт о том, как всё прошло",
        "community_story": "история участника, волонтёра или локации",
        "info": "информационный пост о формате 5 вёрст",
        "announcement": "анонс субботней встречи 5 вёрст",
    }

    platform_hint = (
        "для Telegram: короче, структурировано, можно использовать эмодзи"
        if platform == "telegram"
        else "для ВКонтакте: можно писать чуть подробнее, добавить вопросы и приглашение к комментариям"
    )

    extra_hint = ""
    if post_type == "event_announcement":
        extra_hint = (
            "\n\nЭто пятничное напоминание о субботней встрече. "
            "Обязательно включи в основной текст блок с таймингом по шаблону:\n\n"
            f"{FRIDAY_TIMING_TEMPLATE}\n\n"
            "В конце поста мы отдельно добавим ссылки на регистрацию и схему парка."
        )

    user_content = (
        "Сгенерируй текст для сообщества движения «5 вёрст».\n"
        f"Тип поста: {type_map.get(post_type, 'пост для сообщества 5 вёрст')}.\n"
        f"Площадка: {platform}. Подсказка по стилю: {platform_hint}.\n\n"
        f"Тема/контекст: {topic}\n"
        f"{extra_hint}\n\n"
        "Ориентируйся по стилю и структуре на РЕАЛЬНЫЕ ПРИМЕРЫ в системной инструкции.\n"
        "Пиши как реальный человек, не как бот! Добавь живости, эмодзи в заголовок, личные ощущения.\n"
        "СТРОГО СОБЛЮДАЙ СЛЕДУЮЩУЮ СТРУКТУРУ:\n\n"
        "**Заголовок:** одна короткая строка с 1-2 эмодзи.\n\n"
        "**Основной текст:** 2–4 абзаца простым, дружелюбным языком.\n"
        "Используй живую пунктуацию (!!!, ..., ???), добавь личные впечатления.\n\n"
        "**CTA:** 1–2 понятных призыва к действию (написать в комментариях, прийти в субботу, "
        "записаться волонтёром, поделиться фото).\n\n"
        "**Хештеги:** 1 строка с хештегами вида #5верст и по необходимости локация/тема.\n\n"
        "Не добавляй других разделов и заголовков, только эти четыре блока."
    )

    max_tokens = 400 if platform == "telegram" else 800
    text = await _call_openai(user_content, max_tokens=max_tokens, temperature=0.85)

    # Если нужно, добавляем ТОЛЬКО ссылки, без повторного тайминга
    if post_type == "event_announcement":
        text = f"{text}\n\n{FRIDAY_LINKS_TEMPLATE}"

    return text



async def answer_question(question: str) -> str:
    user_content = (
        "Ты — контент‑ассистент движения «5 вёрст». "
        "Помоги ответить на вопрос по формулировкам, постам и соцсетям.\n\n"
        f"Вопрос: {question}"
    )
    return await _call_openai(user_content, max_tokens=400, temperature=0.7)



async def adapt_for_platform(content: str, target_platform: str = "vk") -> str:
    """
    Адаптация существующего текста под VK или лёгкий рефакторинг.
    """
    if target_platform == "vk":
        instruction = (
            "Адаптируй этот текст под формат поста ВКонтакте для сообщества 5 вёрст.\n"
            "Можно сделать текст немного длиннее, добавить вопросы к аудитории и мягкие приглашения "
            "оставить комментарий, поделиться фото, отметить друзей.\n"
            "Сохрани тон: дружелюбный, простой, без спортивного пафоса.\n"
            "Не добавляй тренировочных советов и не превращай это в соревнование.\n\n"
            f"Исходный текст:\n{content}"
        )
    else:
        instruction = (
            "Немного улучшите и отредактируйте этот текст, сохранив стиль движения 5 вёрст.\n\n"
            f"Текст:\n{content}"
        )

    return await _call_openai(instruction, max_tokens=800, temperature=0.7)
