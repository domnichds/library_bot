from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from ..services.book import get_book_files
from ..models.book import Book, BookFile

async def format_keyboard(book_id: int, genre_id: int, page: int) -> InlineKeyboardMarkup:
    """
    Клавиатура с форматами файлов для выбранной книги.

    - Для каждого файла книги создаётся отдельная кнопка.
    - callback_data кнопок формата имеет вид:
        "download:{file_id}:format:{format}"
      и обрабатывается в on_download.
    - Внизу добавляется кнопка "Назад" для возврата к списку книг
      того же жанра и страницы:
        "genre:{genre_id}:page:{page}"
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


