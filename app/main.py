import asyncio

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

from app.services.file_sync import sync_book_from_fs

from app.config.bot import BOT_TOKEN
from .handlers import book as book_handler
from .handlers import catalog as catalog_handler
from .handlers import main_menu as main_menu_handler
from .handlers import search as search_handler
from .models.db import init_db

bot = Bot(
    token=BOT_TOKEN,
    default=DefaultBotProperties(parse_mode=ParseMode.HTML)
)
dp = Dispatcher()
dp.include_router(catalog_handler.router)
dp.include_router(book_handler.router)
dp.include_router(search_handler.router)
dp.include_router(main_menu_handler.router)


async def main():
    await init_db()
    await sync_book_from_fs()
    try:
        print("Бот запущен. Нажмите ctrl + c для остановки.")
        await dp.start_polling(bot)
    except Exception as e:
        print(f"Ошибка: {e}")

if __name__ == "__main__":
    asyncio.run(main())
