from aiogram import F, Router
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State

from app.services.user_limit import check_daily_limit, increment_daily_count
from app.states.qa import QAStates
from app.texts import (
    QA_ERROR_BAD_REQUEST,
    QA_LIMIT_EXCEEDED,
    QA_ENTER_QUESTION,
    QA_ASKING_SENT
)

router = Router()

@router.callback_query(F.data.regexp(r"^qa:\d+$"))
async def on_ask_question_click(callback: CallbackQuery, state: FSMContext):
    try:
        parts = callback.data.split(":")
        book_id = int(parts[1])
    except (ValueError, IndexError):
        await callback.answer(QA_ERROR_BAD_REQUEST, show_alert=True)
        return
    
    user_id = callback.from_user.id
    can_ask = await check_daily_limit(user_id)
    if not can_ask:
        await callback.answer(QA_LIMIT_EXCEEDED, show_alert=True)
        return
    
    await state.update_data(book_id=book_id)
    await state.set_state(QAStates.waiting_for_question)
    await callback.message.answer(QA_ENTER_QUESTION)
    await callback.answer()

@router.message(QAStates.waiting_for_question)
async def receive_question(message: Message, state: FSMContext):
    user_id = message.from_user.id
    data = await state.get_data()
    book_id = data.get("book_id")

    text = (message.text or "").strip()
    if not text:
        await message.answer(QA_ERROR_BAD_REQUEST)
        return
    
    new_count, status = await increment_daily_count(user_id)
    if not status:
        await message.answer(QA_LIMIT_EXCEEDED)
        await state.clear()
        return
    
    await message.answer(QA_ASKING_SENT)
    await state.clear()

