from aiogram import F, Router
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext

from app.keyboards.catalog import catalog_format_keyboard
from app.keyboards.search import search_format_keyboard
from app.services.user_limit import check_daily_limit, increment_daily_count
from app.states.qa import QAStates
from app.texts import (
    BOOK_SELECT_FORMAT,
    QA_ERROR_BAD_REQUEST,
    QA_LIMIT_EXCEEDED,
    QA_ENTER_QUESTION,
    QA_ASKING_SENT,
)

router = Router()


async def _build_format_keyboard(
    source: str,
    book_id: int,
    genre_id: int | None,
    page: int | None,
):
    if book_id is None:
        return None
    if source == "search":
        return await search_format_keyboard(book_id)
    if source == "catalog" and genre_id is not None and page is not None:
        return await catalog_format_keyboard(book_id, genre_id, page)
    return None


@router.callback_query(F.data.regexp(r"^qa:"))
async def on_ask_question_click(callback: CallbackQuery, state: FSMContext):
    try:
        parts = callback.data.split(":")
        source_raw = parts[1]
        source = {"c": "catalog", "s": "search"}.get(source_raw, source_raw)
        book_id = int(parts[2])
        genre_id = page = None
        if source == "catalog":
            genre_id = int(parts[3])
            page = int(parts[4])
    except (ValueError, IndexError):
        await callback.answer(QA_ERROR_BAD_REQUEST, show_alert=True)
        return

    user_id = callback.from_user.id
    can_ask = await check_daily_limit(user_id)
    if not can_ask:
        await callback.answer(QA_LIMIT_EXCEEDED, show_alert=True)
        return

    await state.set_state(QAStates.waiting_for_question)
    await state.set_data(
        {
            "book_id": book_id,
            "source": source,
            "genre_id": genre_id,
            "page": page,
        }
    )

    await callback.message.answer(QA_ENTER_QUESTION)
    await callback.answer()


@router.message(QAStates.waiting_for_question)
async def receive_question(message: Message, state: FSMContext):
    data = await state.get_data()
    if not data:
        await message.answer(QA_ERROR_BAD_REQUEST)
        return

    book_id = data.get("book_id")
    source = data.get("source")
    genre_id = data.get("genre_id")
    page = data.get("page")

    text = (message.text or "").strip()
    if not text:
        await message.answer(QA_ERROR_BAD_REQUEST)
        return

    count, allowed = await increment_daily_count(message.from_user.id)
    if not allowed:
        await message.answer(QA_LIMIT_EXCEEDED)
        await state.clear()
        return

    keyboard = await _build_format_keyboard(source, book_id, genre_id, page)
    await state.clear()

    if keyboard is None:
        await message.answer(QA_ERROR_BAD_REQUEST)
        return

    await message.answer(QA_ASKING_SENT.format(count=count))
    await message.answer(BOOK_SELECT_FORMAT, reply_markup=keyboard)