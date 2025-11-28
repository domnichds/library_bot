from aiogram import Router, F
from pathlib import Path

from aiogram.types import Message, CallbackQuery, FSInputFile

from app.services.book import get_book_file_path
from app.services.catalog import get_all_genres, get_books_page_by_genre
from app.keyboards.catalog import genres_keyboard, books_keyboard
from app.keyboards.book import format_keyboard

from ..config_storage import BOOKS_DIR_STORAGE
from ..texts import (
    CATALOG_CHOOSE_GENRE,
    CATALOG_NO_BOOKS,
    CATALOG_NO_GENRES,
    CATALOG_CURRENT_GENRE,
    BOOK_SELECT_FORMAT,
)

router = Router()

@router.message(F.text == "📚Каталог")
async def catalog_entery(message: Message):
    """
    Обработчик команды/кнопки «📚Каталог».

    Загружает список жанров из БД и показывает пользователю
    клавиатуру с жанрами. Если жанров нет, выводит соответствующее сообщение.
    """
    genres = await get_all_genres()

    if not genres:
        await message.answer(CATALOG_NO_GENRES)
        return

    await message.answer(
        CATALOG_CHOOSE_GENRE,
        reply_markup=genres_keyboard(genres)
    )

@router.callback_query(F.data.regexp("^genre:\d+:page:\d+$"))
async def on_genre_chosen(callback: CallbackQuery):
    """
    Обработчик выбора жанра или переключения страниц списка книг.

    Ожидаемый формат callback_data:
        "genre:{genre_id}:page:{page}"

    Показывает пользователю список книг выбранного жанра
    с учётом пагинации.
    """
    try:
        parts = callback.data.split(":")
        genre_id = int(parts[1])
        page_id = int(parts[3])
    except (ValueError, IndexError) as e:
        await callback.answer("Ошибка выбора жанра")
        return
    
    # Получаем книги для выбранного жанра и страницы
    books, total_pages = await get_books_page_by_genre(genre_id, page_id)

    if not books:
        await callback.message.edit_text(CATALOG_NO_BOOKS)
        await callback.answer()
        return

    await callback.message.edit_text(
        CATALOG_CURRENT_GENRE,
        reply_markup=books_keyboard(books, genre_id, page_id, total_pages)
    )
    await callback.answer()

@router.callback_query(F.data == "back:genres")
async def on_back_to_genres(callback: CallbackQuery):
    """
    Обработчик кнопки «Назад к жанрам».

    Снова загружает список жанров и заменяет сообщение со списком книг
    на сообщение со списком жанров.
    """
    genres = await get_all_genres()

    # Если жанры были удалены
    if not genres:
        await callback.message.edit_text(CATALOG_NO_GENRES)
        await callback.answer()
        return

    await callback.message.edit_text(
        CATALOG_CHOOSE_GENRE,
        reply_markup=genres_keyboard(genres)
    )
    await callback.answer()

@router.callback_query(F.data.regexp(r"^download:\d+:format:[\w-]+$"))
async def on_download(callback: CallbackQuery):
    """
    Обработчик нажатия на кнопку скачивания файла.

    Ожидаемый формат callback_data:
        "download:{file_id}:format:{format}"

    По id файла и формату находит путь в БД, собирает полный путь
    на диске и отправляет документ пользователю.
    """
    try:
        callback_data_parts = callback.data.split(":")
        book_id = int(callback_data_parts[1])
        book_format = callback_data_parts[3]
    except (ValueError, IndexError):
        await callback.answer("Ошибка в данных для загрузки файла", show_alert=True)
        return

    file_path = await get_book_file_path(book_id, book_format)
    if file_path is None:
        await callback.answer("Файл не найден", show_alert=True)
        return
    
    full_path = BOOKS_DIR_STORAGE / file_path
    file = FSInputFile(full_path, filename=full_path.name)
    await callback.message.answer_document(file, text="Ваш файл готов!")
    await callback.answer()

@router.callback_query(F.data.regexp(r"book:\d+:genre:\d+:page:\d+$"))
async def on_book_chosen(callback: CallbackQuery):
    """
    Обработчик выбора конкретной книги из списка.

    Ожидаемый формат callback_data:
        "book:{book_id}:genre:{genre_id}:page:{page}"

    Показывает пользователю клавиатуру с доступными форматами
    (fb2/pdf и т.п.) для выбранной книги.
    """
    callback_data_parts = callback.data.split(":")
    book_id = int(callback_data_parts[1])
    genre_id = int(callback_data_parts[3])
    page = int(callback_data_parts[5])

    await callback.message.edit_text(
        BOOK_SELECT_FORMAT,
        reply_markup=await format_keyboard(book_id, genre_id, page)
        )
    
    await callback.answer()
    