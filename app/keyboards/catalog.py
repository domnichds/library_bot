from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from ..models.book import Genre, Book


def genres_keyboard(genres: list[Genre]) -> InlineKeyboardMarkup:
    """
    Клавиатура со списком жанров.

    Для каждого жанра создаётся отдельная кнопка:

        "genre:{genre_id}:page:1"

    Страница всегда начинается с 1, дальше пагинацией управляет books_keyboard.
    """
    keyboard: list[list[InlineKeyboardButton]] = []
    for genre in genres:
        keyboard.append(
            [
                InlineKeyboardButton(
                    text=genre.name,
                    callback_data=f"genre:{genre.id}:page:1"
                )
            ]
        )
    return InlineKeyboardMarkup(inline_keyboard=keyboard)
