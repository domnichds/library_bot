from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

def main_menu_keyboard() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="📚Каталог")],
            [KeyboardButton(text="🔍Поиск")]
        ],
        resize_keyboard=True
    )

def back_to_main_menu() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="🏠 В главное меню")]
        ],
        resize_keyboard=True
    )