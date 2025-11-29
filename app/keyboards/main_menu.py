from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

from ..texts import (
    BUTTON_MENU_CATALOG,
    BUTTON_MENU_SEARCH,
    BUTTON_BACK_TO_MAIN_MENU,
)

def main_menu_keyboard() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text=BUTTON_MENU_CATALOG)],
            [KeyboardButton(text=BUTTON_MENU_SEARCH)]
        ],
        resize_keyboard=True
    )

def back_to_main_menu() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text=BUTTON_BACK_TO_MAIN_MENU)]
        ],
        resize_keyboard=True
    )