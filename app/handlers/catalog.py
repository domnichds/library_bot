from aiogram import Router, F

from aiogram.types import Message, CallbackQuery

from app.services.catalog import get_all_genres, get_books_page_by_genre
from app.keyboards.catalog import genres_keyboard, books_keyboard
from ..texts import (
    CATALOG_CHOOSE_GENRE,
    CATALOG_NO_BOOKS,
    CATALOG_NO_GENRES,
    CATALOG_CURRENT_GENRE
)

router = Router()

@router.message(F.text == "📚Каталог")
async def catalog_entery(message: Message):
    genres = await get_all_genres()

    if not genres:
        await message.answer(CATALOG_NO_GENRES)
        return

    await message.answer(
        CATALOG_CHOOSE_GENRE,
        reply_markup=genres_keyboard(genres)
    )

# callback реагирует на выбор жанра
@router.callback_query(F.data.startswith("genre:"))
async def on_genre_chosen(callback: CallbackQuery):
    try:
        genre_id = int(callback.data.split(":")[1])
    except (ValueError, IndexError) as e:
        await callback.answer("Ошибка выбора жанра")
        return
    
    # Получаем книги для выбранного жанра, первую страницу
    books, total_pages = await get_books_page_by_genre(genre_id, 1)

    if not books:
        await callback.message.edit_text(CATALOG_NO_BOOKS)
        await callback.answer()
        return

    await callback.message.edit_text(
        CATALOG_CURRENT_GENRE,
        reply_markup=books_keyboard(books, genre_id, 1, total_pages)
    )
    await callback.answer()

# callback реагирует на возврат к списку жанров
@router.callback_query(F.data == "back:genres")
async def on_back_to_genres(callback: CallbackQuery):
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

