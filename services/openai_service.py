import random

from dotenv import load_dotenv
from openai import AsyncOpenAI, OpenAIError

from config import settings

load_dotenv()

OPENAI_API_KEY = settings.openai_api_key
OPENAI_MODEL = settings.openai_model

client = AsyncOpenAI(api_key=OPENAI_API_KEY)


FRIDAY_TIMING_TEMPLATE = (
    "Напоминаем наше расписание:\n\n"
    "08:30 - сбор и инструктаж волонтёров\n"
    "08:40 - сбор участников\n"
    "08:45 - разминка\n"
    "08:50 - инструктаж новых участников у стелы\n"
    "08:55 - общий брифинг\n"
    "09:00 - старт."
)

FRIDAY_LINKS_TEMPLATE = (
    "Как найти нас в парке: https://5verst.ru/parkmayakovskogo/course/\n\n"
    "Регистрация для тех, кто у нас первый раз: https://5verst.ru/register/"
)

MONDAY_VOLUNTEER_POSITIONS_TEMPLATE = (
    "Свободные позиции:\n"
    "✅ два секундомера\n"
    "✅ сканер\n"
    "✅ раздача карточек позиций\n"
    "✅ маршал\n"
    "✅ замыкающий\n"
    "✅ инструктаж новых участников\n"
    "✅ проверка и разметка трассы\n"
    "✅ фотограф"
)

MONDAY_VOLUNTEER_FOOTER = (
    "Регистрация волонтёров в системе 5 вёрст: https://5verst.ru/register/\n\n"
    "Есть вопросы о волонтёрстве или о конкретных ролях? Напишите в комментариях."
)

STYLE_MODES = {
    "warm": "Теплый и дружелюбный тон. Пиши как живой организатор, который общается со знакомыми людьми.",
    "energetic": "Бодрый и энергичный тон. Динамично, но без канцелярита и без рекламной накачки.",
    "calm": "Спокойный информативный тон. Просто, понятно, по делу, но по-человечески.",
}

FORCED_STYLE_KEY: str | None = None
STYLE_DEBUG_ENABLED = False

BANNED_PHRASES = [
    "друзья, спешим сообщить",
    "не упустите возможность",
    "ждем каждого",
    "с радостью сообщаем",
    "приглашаем всех желающих",
]

SYSTEM_PROMPT = """
Ты - контент-ассистент сообщества 5 вёрст.

Пиши как живой человек, который ведет локальное сообщество.
Текст должен быть естественным, разговорным и понятным.

Запрещено:
- советы по тренировкам, нагрузкам, технике бега;
- медицинские рекомендации;
- называть 5 вёрст тренировкой или соревнованием.

Важно:
- 5 вёрст это бесплатные дружеские еженедельные встречи;
- можно идти пешком или бежать в комфортном темпе;
- сохраняй уважительный, теплый и инклюзивный тон.
""".strip()


async def _call_openai(
    user_content: str,
    max_tokens: int = 700,
    temperature: float = 0.85,
) -> str:
    if not OPENAI_API_KEY:
        return (
            "[ТЕСТОВЫЙ РЕЖИМ БЕЗ OPENAI]\n\n"
            "OPENAI_API_KEY не найден. Проверь файл .env и перезапусти бота."
        )

    try:
        response = await client.chat.completions.create(
            model=OPENAI_MODEL,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_content},
            ],
            temperature=temperature,
            max_tokens=max_tokens,
        )
        return (response.choices[0].message.content or "").strip()
    except OpenAIError as exc:
        return f"Ошибка OpenAI API: {exc}"


def _append_unique_block(text: str, block: str) -> str:
    if block.strip() in text:
        return text
    return f"{text.rstrip()}\n\n{block}"


def get_available_style_keys() -> list[str]:
    return list(STYLE_MODES.keys())


def get_forced_style_key() -> str | None:
    return FORCED_STYLE_KEY


def set_forced_style_key(style_key: str | None) -> None:
    global FORCED_STYLE_KEY
    if style_key is None:
        FORCED_STYLE_KEY = None
        return
    if style_key not in STYLE_MODES:
        raise ValueError(f"Unknown style key: {style_key}")
    FORCED_STYLE_KEY = style_key


def is_style_debug_enabled() -> bool:
    return STYLE_DEBUG_ENABLED


def set_style_debug_enabled(enabled: bool) -> None:
    global STYLE_DEBUG_ENABLED
    STYLE_DEBUG_ENABLED = enabled


def _select_style_mode() -> tuple[str, str]:
    if FORCED_STYLE_KEY and FORCED_STYLE_KEY in STYLE_MODES:
        key = FORCED_STYLE_KEY
    else:
        key = random.choice(list(STYLE_MODES.keys()))
    return key, STYLE_MODES[key]


def _build_generation_prompt(topic: str, post_type: str, platform: str) -> tuple[str, str]:
    style_key, style_instruction = _select_style_mode()

    post_type_desc = {
        "volunteer_call": "понедельничный пост-набор волонтёров",
        "volunteer_thanks": "пост-благодарность волонтёрам после встречи",
        "event_announcement": "пятничное напоминание о субботней встрече",
        "event_report": "короткий отчет о прошедшей встрече",
        "community_story": "история участника, волонтера или локации",
        "info": "информационный пост о формате 5 вёрст",
        "announcement": "анонс субботней встречи",
    }.get(post_type, "пост для сообщества 5 вёрст")

    platform_hint = (
        "Telegram: короче, живее, 2-5 абзацев."
        if platform == "telegram"
        else "VK: можно чуть подробнее, но без лишней воды."
    )

    banned = "\n".join(f"- {phrase}" for phrase in BANNED_PHRASES)

    extra_hint = ""
    if post_type == "event_announcement":
        extra_hint = (
            "Это именно пятничное напоминание. Обязательно добавь блок тайминга В ТОЧНОМ ВИДЕ:\n\n"
            f"{FRIDAY_TIMING_TEMPLATE}\n\n"
            "После этого не добавляй ссылки самостоятельно, они будут добавлены отдельно."
        )
    elif post_type == "volunteer_call":
        extra_hint = (
            "Это понедельничный сбор волонтеров. Нужна структура:\n"
            "1) короткое живое приветствие/контекст;\n"
            "2) список свободных ролей строго в столбик;\n"
            "3) мягкий призыв записаться и написать вопросы в комментариях.\n\n"
            "Пример блока ролей:\n"
            f"{MONDAY_VOLUNTEER_POSITIONS_TEMPLATE}\n\n"
            "Ссылку на регистрацию и финальный вопрос не добавляй, они будут добавлены отдельно."
        )
    elif post_type == "volunteer_thanks":
        extra_hint = (
            "Это пост благодарности волонтёрам после прошедшей встречи.\n"
            "Не превращай его в набор волонтёров.\n"
            "Нужна структура: благодарность, короткое описание вклада команды, теплое приглашение "
            "попробовать себя в волонтёрстве в будущем.\n"
            "Список свободных ролей и формат понедельничного набора здесь не нужны."
        )

    prompt = (
        f"Напиши {post_type_desc}.\n"
        f"Площадка: {platform}. {platform_hint}\n"
        f"Тон: {style_instruction}\n\n"
        f"Контекст/тема:\n{topic}\n\n"
        "Требования к читаемости:\n"
        "- Без служебных заголовков вида 'Заголовок/Основной текст/CTA/Хештеги'.\n"
        "- Короткие абзацы разной длины.\n"
        "- 1-2 эмодзи максимум на весь текст.\n"
        "- Естественный язык, как от человека, без шаблонного ИИ-стиля.\n"
        "- Конкретика важнее общих фраз.\n\n"
        "Не используй эти штампы:\n"
        f"{banned}\n\n"
        f"{extra_hint}"
    )
    return prompt, style_key


async def _humanize_text(draft: str, topic: str, post_type: str, platform: str) -> str:
    user_content = (
        "Отредактируй черновик так, чтобы он звучал как текст живого человека.\n"
        "Сохрани факты и смысл, убери шаблонность и канцелярит.\n"
        "Не добавляй новые выдуманные факты.\n"
        "Сделай ритм текста естественным: короткие и средние фразы, без повторов.\n"
        f"Площадка: {platform}. Тип: {post_type}. Тема: {topic}\n\n"
        f"Черновик:\n{draft}"
    )
    return await _call_openai(user_content, max_tokens=900, temperature=0.75)


async def generate_post(
    topic: str,
    post_type: str = "announcement",
    platform: str = "telegram",
) -> str:
    prompt, style_key = _build_generation_prompt(topic=topic, post_type=post_type, platform=platform)
    draft = await _call_openai(prompt, max_tokens=900, temperature=0.9)
    text = await _humanize_text(draft=draft, topic=topic, post_type=post_type, platform=platform)

    if post_type == "event_announcement":
        text = _append_unique_block(text, FRIDAY_LINKS_TEMPLATE)
    elif post_type == "volunteer_call":
        text = _append_unique_block(text, MONDAY_VOLUNTEER_FOOTER)

    if STYLE_DEBUG_ENABLED:
        text = _append_unique_block(text, f"[style_debug: {style_key}]")

    return text


async def revise_generated_post(
    original_post: str,
    revision_request: str,
    platform: str = "telegram",
) -> str:
    user_content = (
        "Ниже текст поста для сообщества 5 вёрст и просьба пользователя внести правки.\n"
        "Перепиши пост с учетом запроса, сохранив факты, структуру и человечный стиль.\n"
        "Не добавляй выдуманные факты.\n"
        "Если это пост-напоминание или набор волонтеров, сохрани полезные блоки и ссылки, которые уже есть.\n"
        f"Площадка: {platform}\n\n"
        f"Исходный пост:\n{original_post}\n\n"
        f"Запрос на правки:\n{revision_request}\n\n"
        "Верни только итоговый текст поста."
    )
    return await _call_openai(user_content, max_tokens=1000, temperature=0.75)


async def answer_question(question: str) -> str:
    user_content = (
        "Ответь на вопрос организатора 5 вёрст.\n"
        "Дай практичный, короткий и понятный ответ без канцелярита.\n"
        "Можно добавить 2-3 готовые формулировки для поста.\n\n"
        f"Вопрос: {question}"
    )
    return await _call_openai(user_content, max_tokens=500, temperature=0.7)


async def adapt_for_platform(content: str, target_platform: str = "vk") -> str:
    if target_platform == "vk":
        instruction = (
            "Адаптируй текст под формат ВКонтакте для сообщества 5 вёрст.\n"
            "Сделай стиль живым и естественным, без ИИ-штампов и канцелярита.\n"
            "Можно добавить мягкий вопрос в конце для комментариев.\n"
            "Не добавляй тренировочных и медицинских советов.\n\n"
            f"Исходный текст:\n{content}"
        )
    else:
        instruction = (
            "Сделай легкую редактуру текста, чтобы он звучал по-человечески и читался проще.\n\n"
            f"Текст:\n{content}"
        )

    return await _call_openai(instruction, max_tokens=800, temperature=0.75)
