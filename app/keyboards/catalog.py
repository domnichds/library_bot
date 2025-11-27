from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from ..models.book import Genre, Book


def genres_keyboard(genres: list[Genre]) -> InlineKeyboardMarkup:
    keyboard: list[list[InlineKeyboardButton]] = []

    # Загружаем жанры в клавиатуру (предполагается не более 10-15)
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

def books_keyboard(
        books: list[Book],
        genre_id: int,
        page: int,
        total_pages: int,
    ) -> InlineKeyboardMarkup:
    keyboard: list[list[InlineKeyboardButton]] = []

    # Загружаем книги (не более 10) в клавиатуру
    for book in books:
        keyboard.append(
            [
                InlineKeyboardButton(
                    text=f"{book.title} — {book.author}",
                    callback_data=f"book:{book.id}"
                )
            ]
        )
    nav_row: list[InlineKeyboardButton] = []

    # Если не на 1 странице - добавляем кнопку "Назад"
    if page > 1:
        nav_row.append(
            InlineKeyboardButton(
                text="⬅️ Назад",
                callback_data=f"genre:{genre_id}:page:{page - 1}"
            )
        )
    
    # Добавляем кнопку с текущей страницей
    nav_row.append(
        InlineKeyboardButton(
            text=f"{page}/{total_pages}",
            callback_data="noop" # Кнопка без функционала
        )
    )

    # Если не на последней странице - добавляем кнопку "Вперёд"
    if page < total_pages:
        nav_row.append(
            InlineKeyboardButton(
                text="Вперёд ➡️",
                callback_data=f"genre:{genre_id}:page:{page + 1}"
            )
        )
    
    keyboard.append(nav_row)

    # Добавляем кнопку "К жанрам"
    keyboard.append(
        [
            InlineKeyboardButton(
                text="⬅️ К жанрам",
                callback_data="back:genres"
            )
        ]
    )

    return InlineKeyboardMarkup(inline_keyboard=keyboard)