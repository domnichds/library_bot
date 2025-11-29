import asyncio

from aiogram import Bot, Dispatcher, F
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

from app.services.file_sync import sync_book_from_fs
from app.keyboards.main_menu import main_menu_keyboard

from .config import BOT_TOKEN
from .texts import *
from .models.db import init_db

from .handlers import catalog as catalog_handler
from .handlers import book as book_handler
from .handlers import search as search_handler

bot = Bot(
    token=BOT_TOKEN,
    default=DefaultBotProperties(parse_mode=ParseMode.HTML)
)
dp = Dispatcher()
dp.include_router(catalog_handler.router)
dp.include_router(book_handler.router)
dp.include_router(search_handler.router)

@dp.message(F.text == "/start")
async def command_start(message: Message):
    await message.answer(
        START_MESSAGE,
        reply_markup=main_menu_keyboard()
    )

async def main():
    await sync_book_from_fs()
    try:
        print("Бот запущен. Нажмите ctrl + c для остановки")
        await init_db()
        await dp.start_polling(bot)
    except Exception as e:
        print(f"Ошибка: {e}")

if __name__ == "__main__":
    asyncio.run(main())
