from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery

from app.states.search import SearchState
from app.services.search import search_books
from app.keyboards.book import books_search_keyboard

router = Router()

@router.message(F.text == "🔍Поиск")
async def start_search(message: Message, state: FSMContext) -> None:
    await state.set_state(SearchState.waiting_for_query)
    await message.answer("Введите название книги для поиска:")

@router.message(SearchState.waiting_for_query)
async def handle_search_query(message: Message, state: FSMContext) -> None:
    query = message.text.strip()
    if not query:
        await message.answer("Пустой запрос. Попробуйте еще раз")
        return

    books = await search_books(query)
    
    await state.clear()

    if not books:
        await state.set_state(SearchState.waiting_for_query)
        await message.answer(f"По запросу «{query}» ничего не найдено")
        await message.answer("Введите название книги для поиска:")
        return
    
    await message.answer(
        f"Результаты поиска по запросу:\n\n<code>{query}</code>",
        reply_markup=books_search_keyboard(books)
    )

@router.callback_query(F.data == "back:search")
async def on_back_to_search(callback: CallbackQuery, state: FSMContext) -> None:
    await callback.answer()
    await state.set_state(SearchState.waiting_for_query)

    if callback.message:
        await callback.message.edit_text("Введите название книги для поиска:", reply_markup=None)
    else:
        await callback.bot.send_message(callback.from_user.id, "Введите название книги для поиска:")
