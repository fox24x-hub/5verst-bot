from aiogram import Router
from aiogram import types
from aiogram.filters import Command
from services.openai_service import generate_post, adapt_for_platform
from services.stats_service import track_user_action

content_router = Router()



@content_router.message(Command("create_post"))
async def cmd_create_post(message: types.Message):
    """
    Использование:
    /create_post Тема поста
    """
    args = message.text.split(maxsplit=1)
    if len(args) < 2:
        await message.reply(
            "Напишите тему поста после команды.\n\nПример:\n"
            "/create_post Анонс субботнего старта 5 вёрст в нашем парке"
        )
        return

    topic = args[1].strip()

    await message.reply("⏳ Генерирую пост...")
    track_user_action(message.from_user.id, "generate_post")

    post_text = await generate_post(
        topic=topic,
        post_type="announcement",
        platform="telegram",
    )

    await message.reply(post_text)


@content_router.message(Command("adapt_vk"))
async def cmd_adapt_vk(message: types.Message):
    """
    Адаптация текста под VK.
    Работает по reply: нужно ответить на сообщение с текстом и написать /adapt_vk.
    """
    if not message.reply_to_message or not message.reply_to_message.text:
        await message.reply(
            "Ответьте командой /adapt_vk на сообщение с текстом, "
            "который нужно адаптировать под VK."
        )
        return

    original_text = message.reply_to_message.text
    await message.reply("⏳ Адаптирую для VK...")
track_user_action(message.from_user.id, "adapt_vk")

adapted = await adapt_for_platform(original_text, "vk")

    await message.reply(adapted)
