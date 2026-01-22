from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove

# Главная кнопка
main_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="🚀 Помощник")],
    ],
    resize_keyboard=True,
)

# Меню помощника
helper_menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="📝 Создать пост")],
        [KeyboardButton(text="📊 Статистика")],
        [KeyboardButton(text="❓ Спросить GPT")],
        [KeyboardButton(text="🔙 Назад")],
    ],
    resize_keyboard=True,
)

# Меню постов
posts_menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="🧊 Волонтёры"), KeyboardButton(text="🔔 Напоминание")],
        [KeyboardButton(text="📊 Отчёт"), KeyboardButton(text="🙏 Спасибо волонтёрам")],
        [KeyboardButton(text="📝 Свободный пост"), KeyboardButton(text="📝 VK пост")],
        [KeyboardButton(text="🔙 Назад")],
    ],
    resize_keyboard=True,
)

# Убрать клавиатуру
remove_keyboard = ReplyKeyboardRemove()
