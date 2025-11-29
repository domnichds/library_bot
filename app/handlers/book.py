from aiogram import Router, F

from aiogram.types import Message, CallbackQuery, FSInputFile

from app.services.book import get_book_file_path, get_book_name
from app.keyboards.book import search_format_keyboard, catalog_format_keyboard
from app.keyboards.search import search_back_to_main_menu

from ..config_storage import BOOKS_DIR_STORAGE
from ..texts import (
    BOOK_SELECT_FORMAT
)

router = Router()

@router.callback_query(F.data.regexp(r"^download:\d+:format:[\w-]+$"))
async def on_download(callback: CallbackQuery):
    """
    Обработчик нажатия на кнопку скачивания файла.

    Ожидаемый формат callback_data:
        "download:{book_id}:format:{format}"

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

    try:
        await callback.message.delete()
    except Exception:
        pass

    book_name = await get_book_name(book_id)
    await callback.message.answer_document(
        file,
        caption=f"Книга готова к загрузке.\n\n<b>{book_name}</b>",
        reply_markup=search_back_to_main_menu(),
    )
    await callback.answer()

@router.callback_query(F.data.regexp(r"book:\d+:genre:\d+:page:\d+$"))
async def on_catalog_book_chosen(callback: CallbackQuery):
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
        reply_markup=await catalog_format_keyboard(book_id, genre_id, page)
        )
    
    await callback.answer()

@router.callback_query(F.data.regexp(r"book:\d+$"))
async def on_search_book_chosen(callback: CallbackQuery):
    callback_data_parts = callback.data.split(":")
    book_id = int(callback_data_parts[1])

    await callback.message.edit_text(
        BOOK_SELECT_FORMAT,
        reply_markup=await search_format_keyboard(book_id)
        )
    
    await callback.answer()