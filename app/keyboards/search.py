from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from ..models.book import Book

def search_back_to_main_menu() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="🏠В главное меню", callback_data="menu:main")]
        ]
    )