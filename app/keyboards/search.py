from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from ..models.book import Book
from ..services.book import get_book_files


def books_search_keyboard(books: list[Book]) -> InlineKeyboardMarkup:
    """
    Клавиатура с результатами поиска.

    Каждая книга -> кнопка:
        "book:{book_id}"
    """
    keyboard: list[list[InlineKeyboardButton]] = []
    
    for book in books:
        keyboard.append(
            [
                InlineKeyboardButton(
                    text=f"{book.title} — {book.author}",
                    callback_data=f"book:{book.id}"
                )
            ]
        )
    
    keyboard.append(
        [
            InlineKeyboardButton(
                text="⬅️ К поиску",
                callback_data="back:search"
            )
        ]
    )

    return InlineKeyboardMarkup(inline_keyboard=keyboard)

async def search_format_keyboard(book_id: int) -> InlineKeyboardMarkup:
    """
    Клавиатура с форматами файлов для выбранной книги.

    - Для каждого файла книги создаётся отдельная кнопка.
    - callback_data кнопок формата имеет вид:
        "download:{book_id}:format:{format}"
      и обрабатывается в on_download.
    - Внизу добавляется кнопка "Назад" для возврата к поиску:
        "back:search"
    """
    keyboard: list[list[InlineKeyboardButton]] = []
    
    book_files = await get_book_files(book_id)
    if len(book_files) == 0:
        keyboard.append(
            [
                InlineKeyboardButton(
                    text="Нет доступных файлов",
                    callback_data="noop"
                )
            ]
        )
    else:
        for book_file in book_files:
            keyboard.append(
                [
                    InlineKeyboardButton(
                        text=book_file.format,
                        callback_data=f"download:{book_id}:format:{book_file.format}"
                    )
                ]
            )
    keyboard.append(
        [
            InlineKeyboardButton(
                text="⬅️ К поиску",
                callback_data=f"back:search"
            )
        ]
    )

    return InlineKeyboardMarkup(inline_keyboard=keyboard)
