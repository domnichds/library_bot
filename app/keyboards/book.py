from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from ..services.book import get_book_files
from ..models.book import Book

async def catalog_format_keyboard(book_id: int, genre_id: int, page: int) -> InlineKeyboardMarkup:
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
                        callback_data=f"download:{book_id}:format:{book_file.format}"
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
                text="⬅️ Назад",
                callback_data=f"back:search"
            )
        ]
    )

    return InlineKeyboardMarkup(inline_keyboard=keyboard)

def books_catalog_keyboard(
        books: list[Book],
        genre_id: int,
        page: int,
        total_pages: int,
    ) -> InlineKeyboardMarkup:
    keyboard: list[list[InlineKeyboardButton]] = []
    """
    Клавиатура со списком книг конкретного жанра + элементы пагинации.

    - Каждая книга -> отдельная кнопка:
        "book:{book_id}:genre:{genre_id}:page:{page}"
      Здесь genre_id и page нужны, чтобы при выборе книги потом
      можно было корректно вернуться назад на тот же список.

    - Внизу добавляется ряд с пагинацией:
        [ "⬅️ Назад", "{page}/{total_pages}", "Вперёд ➡️" ]
      Кнопки "Назад"/"Вперёд" меняют только номер страницы:
        "genre:{genre_id}:page:{page-1}" / "genre:{genre_id}:page:{page+1}"

    - Ещё ниже — кнопка "⬅️ К жанрам" для возврата к списку жанров.
    """
    for book in books:
        keyboard.append(
            [
                InlineKeyboardButton(
                    text=f"{book.title} — {book.author}",
                    callback_data=f"book:{book.id}:genre:{genre_id}:page:{page}"
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
