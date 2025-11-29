from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

def main_menu_keyboard() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="📚Каталог")],
            [KeyboardButton(text="🔍Поиск")]
        ],
        resize_keyboard=True
    )