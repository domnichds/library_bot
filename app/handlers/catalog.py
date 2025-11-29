from aiogram import Router, F

from aiogram.types import Message, CallbackQuery

from app.services.catalog import get_all_genres, get_books_page_by_genre
from app.keyboards.catalog import genres_keyboard
from app.keyboards.book import books_catalog_keyboard

from ..texts import (
    CATALOG_CHOOSE_GENRE,
    CATALOG_NO_BOOKS,
    CATALOG_NO_GENRES,
    CATALOG_CURRENT_GENRE
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
        reply_markup=books_catalog_keyboard(books, genre_id, page_id, total_pages)
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
