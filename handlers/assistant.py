import os
import json
from datetime import datetime

from aiogram import Router, F, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State


from keyboards import main_keyboard, helper_menu, posts_menu, remove_keyboard, templates_keyboard
from services.openai_service import generate_post, answer_question
from services.stats_service import track_user_action


assistant_router = Router()

# ========= FSM состояния =========

class AddExampleStates(StatesGroup):
    waiting_example = State()


class ToneSettingsStates(StatesGroup):
    waiting_tone_choice = State()


class ReportStates(StatesGroup):
    waiting_total = State()
    waiting_first_timers = State()
    waiting_guests = State()
    waiting_volunteers = State()
    waiting_highlight = State()


# ========= файлы с данными =========

EXAMPLES_FILE = "data/posts_examples.json"
SETTINGS_FILE = "data/user_settings.json"
os.makedirs("data", exist_ok=True)


def load_examples():
    if os.path.exists(EXAMPLES_FILE):
        with open(EXAMPLES_FILE, "r", encoding="utf-8") as f:
            try:
                return json.load(f)
            except Exception:
                return []
    return []


def save_examples(examples):
    with open(EXAMPLES_FILE, "w", encoding="utf-8") as f:
        json.dump(examples, f, ensure_ascii=False, indent=2)


def load_user_settings(user_id: int):
    if os.path.exists(SETTINGS_FILE):
        try:
            with open(SETTINGS_FILE, "r", encoding="utf-8") as f:
                all_settings = json.load(f)
                return all_settings.get(str(user_id), {"tone": "neutral"})
        except Exception:
            return {"tone": "neutral"}
    return {"tone": "neutral"}


def save_user_settings(user_id: int, settings: dict):
    all_settings = {}
    if os.path.exists(SETTINGS_FILE):
        try:
            with open(SETTINGS_FILE, "r", encoding="utf-8") as f:
                all_settings = json.load(f)
        except Exception:
            pass
    all_settings[str(user_id)] = settings
    with open(SETTINGS_FILE, "w", encoding="utf-8") as f:
        json.dump(all_settings, f, ensure_ascii=False, indent=2)


# ========= простые флаги состояний =========

waiting_free_topic_tg: set[int] = set()
waiting_free_topic_vk: set[int] = set()


# ========= главное меню и панель =========

@assistant_router.message(Command("start", "panel", "help"))
async def show_main_menu(message: types.Message):
    await message.answer(
        "🚀 **5 ВЁРСТ — Помощник контента**\n\n"
        "Создавай посты, управляй волонтёрами и развивай сообщество!",
        reply_markup=main_keyboard,
        parse_mode="Markdown",
    )


@assistant_router.message(Command("panel"))
async def show_panel(message: types.Message):
    await message.answer(
        "Выбери шаблон поста:",
        reply_markup=templates_keyboard,
    )


@assistant_router.message(F.text == "🔙 Назад")
async def go_back(message: types.Message):
    await message.answer("Главное меню:", reply_markup=main_keyboard)


@assistant_router.message(F.text == "🚀 Помощник")
async def show_helper_menu(message: types.Message):
    await message.answer("Что нужно сделать?", reply_markup=helper_menu)


@assistant_router.message(F.text == "📝 Создать пост")
async def show_posts_menu(message: types.Message):
    await message.answer("Выбери тип поста:", reply_markup=posts_menu)


@assistant_router.message(F.text == "📊 Статистика")
async def stats_shortcut(message: types.Message):
    await cmd_stats_posts(message)


@assistant_router.message(F.text == "❓ Спросить GPT")
async def ask_shortcut(message: types.Message):
    await message.answer(
        "💡 Напиши вопрос после /ask:\n\n"
        "/ask Как сделать пост про волонтёров?",
        reply_markup=main_keyboard,
    )


# ========= кнопки с готовыми шаблонами =========

@assistant_router.message(F.text == "🧊 Волонтёры")
async def monday_volunteers(message: types.Message):
    topic = "Пост понедельник: сбор команды волонтёров на встречу 5 вёрст."
    text = await generate_post(topic=topic, post_type="volunteer_call", platform="telegram")
    await message.answer(text, reply_markup=main_keyboard)


@assistant_router.message(F.text == "🔔 Напоминание")
async def friday_reminder(message: types.Message):
    topic = "Пост пятница: напоминание о встречу 5 вёрст."
    text = await generate_post(topic=topic, post_type="event_announcement", platform="telegram")
    await message.answer(text, reply_markup=main_keyboard)


@assistant_router.message(F.text == "🙏 Спасибо волонтёрам")
async def sunday_thanks(message: types.Message):
    topic = "Благодарность волонтёрам за помощь."
    text = await generate_post(topic=topic, post_type="volunteer_call", platform="telegram")
    await message.answer(text, reply_markup=main_keyboard)


@assistant_router.message(F.text == "🧊 Пн: волонтёры")
async def monday_volunteers_template(message: types.Message):
    topic = (
        "Пост понедельник: сбор команды волонтёров на ближайшую субботнюю встречу "
        "5 вёрст. Вступление через погоду и настроение недели, затем список позиций "
        "волонтёров и приглашение записаться в комментариях."
    )
    text = await generate_post(topic=topic, post_type="volunteer_call", platform="telegram")
    await message.answer(text)


@assistant_router.message(F.text == "🔔 Пт: напоминание")
async def friday_reminder_template(message: types.Message):
    topic = (
        "Пост пятница: напоминание участникам о завтрашней встрече 5 вёрст. "
        "Напомни время, место, формат (можно идти пешком), предложи взять друзей "
        "и написать в комментариях, кто придёт."
    )
    text = await generate_post(topic=topic, post_type="event_announcement", platform="telegram")
    await message.answer(text)


@assistant_router.message(F.text == "🙏 Вс: спасибо волонтёрам")
async def sunday_thanks_template(message: types.Message):
    topic = (
        "Пост воскресенье: благодарность волонтёрам за прошедшую встречу 5 вёрст. "
        "Подчеркни, что без волонтёров встреча бы не состоялась, перечисли роли и пригласи "
        "новых людей попробовать себя в волонтёрстве."
    )
    text = await generate_post(topic=topic, post_type="volunteer_call", platform="telegram")
    await message.answer(text)


# ========= FSM отчёта =========

@assistant_router.message(F.text == "📊 Отчёт")
@assistant_router.message(F.text == "📊 Сб: отчёт")
async def saturday_report_start(message: types.Message, state: FSMContext):
    await state.set_state(ReportStates.waiting_total)
    await message.answer(
        "📊 Давай сделаем отчёт о встрече.\n\n"
        "Сколько было участников всего?",
        reply_markup=remove_keyboard,
    )


@assistant_router.message(ReportStates.waiting_total)
async def report_total(message: types.Message, state: FSMContext):
    if not message.text.isdigit():
        await message.answer("Отправь число участников (только цифры).")
        return
    await state.update_data(total=int(message.text))
    await state.set_state(ReportStates.waiting_first_timers)
    await message.answer("Сколько были впервые?")


@assistant_router.message(ReportStates.waiting_first_timers)
async def report_first_timers(message: types.Message, state: FSMContext):
    if not message.text.isdigit():
        await message.answer("Отправь число новичков (только цифры).")
        return
    await state.update_data(first_timers=int(message.text))
    await state.set_state(ReportStates.waiting_guests)
    await message.answer("Сколько гостей из других локаций?")


@assistant_router.message(ReportStates.waiting_guests)
async def report_guests(message: types.Message, state: FSMContext):
    if not message.text.isdigit():
        await message.answer("Отправь число гостей (только цифры).")
        return
    await state.update_data(guests=int(message.text))
    await state.set_state(ReportStates.waiting_volunteers)
    await message.answer("Сколько волонтёров помогали?")


@assistant_router.message(ReportStates.waiting_volunteers)
async def report_volunteers(message: types.Message, state: FSMContext):
    if not message.text.isdigit():
        await message.answer("Отправь число волонтёров (только цифры).")
        return
    await state.update_data(volunteers=int(message.text))
    await state.set_state(ReportStates.waiting_highlight)
    await message.answer("Особенный момент встречи? (или напиши 'нет')")


@assistant_router.message(ReportStates.waiting_highlight)
async def report_highlight(message: types.Message, state: FSMContext):
    data = await state.get_data()
    await state.clear()

    total = data.get("total", 0)
    first_timers = data.get("first_timers", 0)
    guests = data.get("guests", 0)
    volunteers = data.get("volunteers", 0)
    highlight = "" if message.text.lower() == "нет" else message.text.strip()

    topic = (
        f"Отчёт встречи: {total} участников, {first_timers} новичков, "
        f"{guests} гостей, {volunteers} волонтёров."
    )
    if highlight:
        topic += f"\nОсобенный момент: {highlight}"

    text = await generate_post(topic=topic, post_type="event_report", platform="telegram")
    await message.answer(text, reply_markup=main_keyboard)


# ========= свободные посты =========

@assistant_router.message(F.text == "📝 Свободный пост")
async def free_post_telegram(message: types.Message):
    waiting_free_topic_tg.add(message.from_user.id)
    await message.answer(
        "Напиши тему или черновой текст поста для Telegram.\n"
        "Я сделаю из него готовый пост 5 вёрст.",
        reply_markup=remove_keyboard,
    )


@assistant_router.message(F.text == "📝 Свободный пост (VK)")
@assistant_router.message(F.text == "📝 VK пост")
async def free_post_vk(message: types.Message):
    waiting_free_topic_vk.add(message.from_user.id)
    await message.answer(
        "Напиши тему или черновой текст поста для ВКонтакте.\n"
        "Я сделаю из него готовый пост 5 вёрст.",
        reply_markup=remove_keyboard,
    )


# ========= работа с примерами и тоном =========

@assistant_router.message(Command("add_example"))
async def cmd_add_example(message: types.Message, state: FSMContext):
    await state.set_state(AddExampleStates.waiting_example)
    await message.answer("📚 Отправь пример удачного поста для обучения.")


@assistant_router.message(AddExampleStates.waiting_example)
async def save_example(message: types.Message, state: FSMContext):
    if message.text.startswith("/"):
        await state.clear()
        return

    examples = load_examples()
    examples.append(
        {
            "text": message.text,
            "added_at": datetime.now().isoformat(),
            "user_id": message.from_user.id,
        }
    )
    save_examples(examples)
    await state.clear()
    await message.answer(
        f"✅ Пример сохранён! Всего: {len(examples)}",
        reply_markup=main_keyboard,
    )


@assistant_router.message(Command("tone_settings"))
async def cmd_tone_settings(message: types.Message, state: FSMContext):
    current_settings = load_user_settings(message.from_user.id)
    current_tone = current_settings.get("tone", "neutral")

    keyboard = types.ReplyKeyboardMarkup(
        keyboard=[
            [types.KeyboardButton(text="🔥 Теплый")],
            [types.KeyboardButton(text="📊 Информативный")],
            [types.KeyboardButton(text="😄 С юмором")],
            [types.KeyboardButton(text="⚖️ Нейтральный")],
        ],
        resize_keyboard=True,
    )

    await state.set_state(ToneSettingsStates.waiting_tone_choice)
    await message.answer(
        f"🎨 Выбери тон (текущий: {current_tone}):",
        reply_markup=keyboard,
    )


@assistant_router.message(ToneSettingsStates.waiting_tone_choice)
async def set_tone(message: types.Message, state: FSMContext):
    tone_map = {
        "🔥 Теплый": "warm",
        "📊 Информативный": "info",
        "😄 С юмором": "humor",
        "⚖️ Нейтральный": "neutral",
    }
    tone = tone_map.get(message.text, "neutral")
    settings = load_user_settings(message.from_user.id)
    settings["tone"] = tone
    save_user_settings(message.from_user.id, settings)
    await state.clear()
    await message.answer(f"✅ Тон: {message.text}", reply_markup=main_keyboard)


@assistant_router.message(Command("stats_examples"))
async def cmd_stats_examples(message: types.Message):
    examples = load_examples()
    user_settings = load_user_settings(message.from_user.id)
    await message.answer(
        f"📊 Примеров: {len(examples)}\n🎨 Тон: {user_settings.get('tone', 'neutral')}",
        reply_markup=main_keyboard,
    )


async def cmd_stats_posts(message: types.Message):
    await cmd_stats_examples(message)


# ========= команды /ask и help =========

@assistant_router.message(Command("ask"))
async def cmd_ask(message: types.Message):
    args = message.text.split(maxsplit=1)
    if len(args) < 2:
        await message.answer(
            "Напишите ваш вопрос после команды.\n\nПример:\n"
            "/ask Как мягко пригласить людей стать волонтёрами?",
            reply_markup=main_keyboard,
        )
        return

    question = args[1].strip()
    await message.reply("🤔 Думаю над ответом...")
    answer = await answer_question(question)
    await message.reply(answer, reply_markup=main_keyboard)


@assistant_router.message(Command("help"))
async def cmd_help(message: types.Message):
    await message.reply(
        "📚 КОМАНДЫ БОТА 5 ВЁРСТ\n\n"
        "/create_post Тема поста\n"
        "→ Сгенерировать пост.\n\n"
        "/ask Вопрос\n"
        "→ Задать вопрос по формулировкам, постам и соцсетям.\n\n"
        "/adapt_vk (по ответу на сообщение)\n"
        "→ Адаптировать текст под формат ВКонтакте.\n\n"
        "/panel\n"
        "→ Показать кнопки с шаблонами постов.",
    )

# ========= admin statistics command =========
@assistant_router.message(Command("users_stats"))
async def cmd_users_stats(message: types.Message):
    """
    Show usage statistics only for admin
    """
    from services.stats_service import ADMIN_ID, format_stats_report
    
    if message.from_user.id != ADMIN_ID:
        await message.answer(
            "❌ This command is only available for administrator."
        )
        return
    
    report = format_stats_report()
    await message.answer(report, parse_mode="Markdown")

@assistant_router.message(Command("dump_examples"))
async def cmd_dump_examples(message: types.Message):
        """
            Send posts_examples.json as file for admin only
                """
        from services.stats_service import ADMIN_ID

    if message.from_user.id != ADMIN_ID:
                await message.answer(
                                "❌ This command is only available for administrator."
                            )
                return

    if not os.path.exists(EXAMPLES_FILE):
                await message.answer("📄 posts_examples.json not found. Please add examples first.")
                return

    try:
                with open(EXAMPLES_FILE, "rb") as f:
                                await message.answer_document(
                                                    types.FSInputFile(EXAMPLES_FILE),
                                                    caption="💾 posts_examples.json backup"
                                                )
                        except Exception as e:
                                    await message.answer(f"❌ Error sending file: {str(e)}")

# ========= универсальный хендлер =========

@assistant_router.message()
async def universal_handler(message: types.Message):
    user_id = message.from_user.id

    if user_id in waiting_free_topic_tg:
        waiting_free_topic_tg.discard(user_id)
        topic = message.text.strip()
        text = await generate_post(
            topic=topic,
            post_type="announcement",
            platform="telegram",
        )
        await message.answer(text, reply_markup=main_keyboard)
        return

    if user_id in waiting_free_topic_vk:
        waiting_free_topic_vk.discard(user_id)
        topic = message.text.strip()
        text = await generate_post(
            topic=topic,
            post_type="announcement",
            platform="vk",
        )
        await message.answer(text, reply_markup=main_keyboard)
        return

    if message.text.startswith("/ask"):
        await cmd_ask(message)
        return

    if message.text == "/stats_posts":
        await cmd_stats_posts(message)
        return

    await message.answer(
        "Не понял команду. Используй кнопки:",
        reply_markup=main_keyboard,
    )



