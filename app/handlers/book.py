from aiogram import F, Router
from aiogram.types import CallbackQuery, FSInputFile

from app.keyboards.catalog import catalog_format_keyboard
from app.keyboards.search import search_format_keyboard
from app.services.book import get_book_file_path, get_book_name

from ..config.storage import BOOKS_DIR_STORAGE
from ..texts import (
    BOOK_SELECT_FORMAT,
    BOOK_DOWNLOAD_ERROR_DATA_NOT_FOUND,
    BOOK_DOWNLOAD_ERROR_FILE_NOT_FOUND,
    BOOK_READY_CAPTION,
    BOOK_SENDING_IN_PROGRESS,
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
        await callback.answer(BOOK_DOWNLOAD_ERROR_DATA_NOT_FOUND, show_alert=True)
        return
    file_path = await get_book_file_path(book_id, book_format)
    if file_path is None:
        await callback.answer(BOOK_DOWNLOAD_ERROR_FILE_NOT_FOUND, show_alert=True)
        return
    
    full_path = BOOKS_DIR_STORAGE / file_path
    file = FSInputFile(full_path, filename=full_path.name)

    try:
        await callback.message.delete()
    except Exception:
        pass
    
    status_message = None
    try:
        status_message = await callback.message.answer(BOOK_SENDING_IN_PROGRESS)
    except Exception:
        pass

    book_name = await get_book_name(book_id)
    try:
        await callback.message.answer_document(
            file,
            caption=BOOK_READY_CAPTION.format(book_name=book_name)
        )
    finally:
        if status_message is not None:
            try:
                await status_message.delete()
            except Exception:
                pass
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
    """
    Обработчик выбора книги из поиска: показывает доступные форматы и подтверждает колбэк.

    Ожидаемый формат callback_data:
        "book:{book_id}"
    
    Показывает пользователю клавиатуру с доступными форматами
    (fb2/pdf и т.п.) для выбранной книги.
    """
    callback_data_parts = callback.data.split(":")
    book_id = int(callback_data_parts[1])

    await callback.message.edit_text(
        BOOK_SELECT_FORMAT,
        reply_markup=await search_format_keyboard(book_id)
        )
    
    await callback.answer()