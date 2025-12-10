from aiogram import F, Router
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext

from app.keyboards.catalog import catalog_format_keyboard
from app.keyboards.search import search_format_keyboard
from app.services.book import get_book_name
from app.services.llm import LLMError, ask_book_question
from app.services.user_limit import (
    DAILY_LIMIT,
    check_daily_limit,
    increment_daily_count,
)
from app.states.qa import QAStates
from app.texts import (
    BOOK_SELECT_FORMAT,
    QA_ERROR_BAD_REQUEST,
    QA_LIMIT_EXCEEDED,
    QA_ENTER_QUESTION,
    QA_ASKING_SENT,
    QA_QUESTION_TOO_LONG,
    QA_IN_PROGRESS,
    QA_RESPONSE_READY,
)

router = Router()


async def _build_format_keyboard(
    source: str,
    book_id: int,
    genre_id: int | None,
    page: int | None,
):
    """
    Генерирует клавиатуру для возврата в зависимости от типа
    предшествующего окна
    """
    if book_id is None:
        return None
    if source == "search":
        return await search_format_keyboard(book_id)
    if source == "catalog" and genre_id is not None and page is not None:
        return await catalog_format_keyboard(book_id, genre_id, page)
    return None


async def _return_to_format_keyboard(
    message: Message,
    source: str,
    book_id: int,
    genre_id: int | None,
    page: int | None,
):
    """
    Возвращает пользователя к клавиатуре выбора формата книги
    после обработки вопроса
    """
    keyboard = await _build_format_keyboard(source, book_id, genre_id, page)
    if keyboard is None:
        await message.answer(QA_ERROR_BAD_REQUEST)
        return False

    await message.answer(BOOK_SELECT_FORMAT, reply_markup=keyboard)
    return True


@router.callback_query(F.data.regexp(r"^qa:"))
async def on_ask_question_click(callback: CallbackQuery, state: FSMContext):
    """
    Обработчик нажатия на кнопку «Спросить у YandexGPT».
    Разбивает callback_data, проверяет лимит запросов пользователя
    и переводит пользователя в состояние ввода вопроса.
    """
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
    """
    Обрабатывает вопрос о книге: проверяет ввод и дневной лимит.
    Затем запрашивает ответ у LLM и возвращает к выбору формата.
    """
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
        await _return_to_format_keyboard(
            message, source, book_id, genre_id, page
        )
        await state.clear()
        return

    if len(text) > 300:
        await message.answer(QA_QUESTION_TOO_LONG)
        await _return_to_format_keyboard(
            message, source, book_id, genre_id, page
        )
        await state.clear()
        return

    processing_message = await message.answer(QA_IN_PROGRESS)

    try:
        count, allowed = await increment_daily_count(message.from_user.id)
        if not allowed:
            await message.answer(QA_LIMIT_EXCEEDED)
            await _return_to_format_keyboard(
                message, source, book_id, genre_id, page
            )
            await state.clear()
            return

        book_name = await get_book_name(book_id)
        try:
            answer = await ask_book_question(book_name, text)
        except LLMError:
            await message.answer(QA_ERROR_BAD_REQUEST)
            await _return_to_format_keyboard(
                message, source, book_id, genre_id, page
            )
            await state.clear()
            return

        keyboard = await _build_format_keyboard(source, book_id, genre_id, page)
        await state.clear()

        if keyboard is None:
            await message.answer(QA_ERROR_BAD_REQUEST)
            return

        await message.answer(
            QA_RESPONSE_READY.format(book_name=book_name, answer=answer),
        )
        await message.answer(
            QA_ASKING_SENT.format(count=count, total=DAILY_LIMIT),
        )
        await message.answer(BOOK_SELECT_FORMAT, reply_markup=keyboard)
    finally:
        try:
            await processing_message.delete()
        except Exception:
            pass