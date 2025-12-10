from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from app.keyboards.main_menu import back_to_main_menu, main_menu_keyboard
from app.keyboards.search import books_search_keyboard
from app.services.search import search_books
from app.states.search import SearchState
from app.texts import (
    START_MESSAGE,
    BUTTON_MENU_SEARCH,
    BUTTON_BACK_TO_MAIN_MENU,
    SEARCH_PROMPT,
    SEARCH_EMPTY_QUERY,
    SEARCH_NO_RESULTS,
    SEARCH_RESULT,
)

router = Router()


@router.message(F.text == BUTTON_MENU_SEARCH)
async def start_search(message: Message, state: FSMContext) -> None:
    """
    Обработчик команды/кнопки «🔍 Поиск».

    Вводит пользователя в режим поиска книг.
    """
    await state.set_state(SearchState.waiting_for_query)
    await message.answer(
        SEARCH_PROMPT,
        reply_markup=back_to_main_menu(),
    )


@router.message(SearchState.waiting_for_query)
async def handle_search_query(message: Message, state: FSMContext) -> None:
    """
    Обрабатывает введённый пользователем поисковый запрос.

    - Переходит в состояние ожидания нового запроса, если ничего не найдено.
    - Игнорирует сообщение о возврате в главное меню.
    """
    query = (message.text or "").strip()

    if query == BUTTON_BACK_TO_MAIN_MENU:
        await state.clear()
        await message.answer(
            START_MESSAGE,
            reply_markup=main_menu_keyboard(),
        )
        return

    if not query:
        await message.answer(SEARCH_EMPTY_QUERY)
        return

    books = await search_books(query)

    await state.clear()

    if not books:
        await state.set_state(SearchState.waiting_for_query)
        await message.answer(SEARCH_NO_RESULTS.format(query=query))
        await message.answer(
            SEARCH_PROMPT,
            reply_markup=back_to_main_menu(),
        )
        return

    await message.answer(
        SEARCH_RESULT.format(query=query),
        reply_markup=books_search_keyboard(books),
    )


@router.callback_query(F.data == "back:search")
async def on_back_to_search(callback: CallbackQuery, state: FSMContext) -> None:
    """
    Возвращает пользователя к вводу поискового запроса.
    """
    await callback.answer()
    await state.set_state(SearchState.waiting_for_query)

    if callback.message:
        await callback.message.delete()

    await callback.bot.send_message(
        callback.from_user.id,
        SEARCH_PROMPT,
        reply_markup=back_to_main_menu(),
    )
