from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from app.keyboards.main_menu import main_menu_keyboard
from app.texts import START_MESSAGE

router = Router()

@router.message(F.text == "/start")
@router.message(F.text == "🏠 В главное меню")
async def back_to_main_menu_handler(message: Message, state: FSMContext) -> None:
    """
    Сбрасывает состояние пользователя и возвращает его в главное меню.
    """
    await state.clear()
    await message.answer(
        START_MESSAGE,
        reply_markup=main_menu_keyboard()
    )