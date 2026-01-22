from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

templates_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="🧊 Пн: волонтёры"),
            KeyboardButton(text="🔔 Пт: напоминание"),
        ],
        [
            KeyboardButton(text="📊 Сб: отчёт"),
            KeyboardButton(text="🙏 Вс: спасибо волонтёрам"),
        ],
        [
            KeyboardButton(text="📝 Свободный пост"),
            KeyboardButton(text="📝 Свободный пост (VK)"),
        ],
    ],
    resize_keyboard=True,
)
