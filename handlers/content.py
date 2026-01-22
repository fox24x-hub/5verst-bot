from aiogram import Router, types, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext  # если используешь FSM

from services.openai_service import generate_post
from keyboards.main import main_keyboard  # если нужно

router = Router()  # обязательно до декораторов

@router.message(Command("create_post"))
async def cmd_create_post(message: types.Message):
    ...

    """
    Простая версия: /create_post Текст темы
    Потом можно усложнить типами постов.
    """
    args = message.text.split(maxsplit=1)
    if len(args) < 2:
        await message.reply(
            "Напишите тему поста после команды.\n\nПример:\n"
            "/create_post Анонс субботнего старта 5 вёрст в нашем парке"
        )
        return

    topic = args[1].strip()

    await message.reply("⏳ Генерирую тестовый пост (пока без GPT)...")

    post_text = await generate_post(topic, post_type="announcement", platform="telegram")

    await message.reply(post_text)


@router.message(Command("adapt_vk"))
async def cmd_adapt_vk(message: types.Message):
    """
    Адаптация текста под VK.
    Работает по reply: нужно ответить на сообщение с текстом команды /adapt_vk
    """
    if not message.reply_to_message or not message.reply_to_message.text:
        await message.reply(
            "Ответьте командой /adapt_vk на сообщение с текстом, который нужно адаптировать под VK."
        )
        return

    original_text = message.reply_to_message.text
    await message.reply("⏳ Адаптирую для VK (тестовый режим)...")

    adapted = await adapt_for_platform(original_text, "vk")

    await message.reply(adapted)

# handlers/content.py

from aiogram import Router, types
from aiogram.filters import Command
from services.openai_service import generate_post, adapt_for_platform




@router.message(Command("create_post"))
async def cmd_create_post(message: types.Message):
    """
    Простая версия: /create_post Текст темы
    Потом можно усложнить типами постов.
    """
    args = message.text.split(maxsplit=1)
    if len(args) < 2:
        await message.reply(
            "Напишите тему поста после команды.\n\nПример:\n"
            "/create_post Анонс субботнего старта 5 вёрст в нашем парке"
        )
        return

    topic = args[1].strip()

    await message.reply("⏳ Генерирую тестовый пост (пока без GPT)...")

    post_text = await generate_post(topic, post_type="announcement", platform="telegram")

    await message.reply(post_text)


@router.message(Command("adapt_vk"))
async def cmd_adapt_vk(message: types.Message):
    """
    Адаптация текста под VK.
    Работает по reply: нужно ответить на сообщение с текстом команды /adapt_vk
    """
    if not message.reply_to_message or not message.reply_to_message.text:
        await message.reply(
            "Ответьте командой /adapt_vk на сообщение с текстом, который нужно адаптировать под VK."
        )
        return

    original_text = message.reply_to_message.text
    await message.reply("⏳ Адаптирую для VK (тестовый режим)...")

    adapted = await adapt_for_platform(original_text, "vk")

    await message.reply(adapted)

