from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from ..services.book import get_book_files
from ..models.book import Book, BookFile

async def format_keyboard(book_id: int, genre_id: int, page: int) -> InlineKeyboardMarkup:
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
                        callback_data=f"download:{book_file.id}:format:{book_file.format}"
                    )
                ]
            )
        keyboard.append(
            [
                InlineKeyboardButton(
                    text="⬅️ Назад",
                    callback_data=f"genre:{genre_id}:page:{page}"
                )
            ]
        )

    return InlineKeyboardMarkup(inline_keyboard=keyboard)


