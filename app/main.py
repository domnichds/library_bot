import asyncio

from aiogram import Bot, Dispatcher, F
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

from config import BOT_TOKEN
from texts import *
bot = Bot(
    token=BOT_TOKEN,
    default=DefaultBotProperties(parse_mode=ParseMode.HTML)
)
dp = Dispatcher()

def main_menu_keyboard() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="📚Каталог")],
            [KeyboardButton(text="🔍Поиск")]
        ], resize_keyboard=True
    )

@dp.message(F.text == "/start")
async def command_start(message: Message):
    await message.answer(
        START_MESSAGE, reply_markup=main_menu_keyboard()
    )

async def main():
    try:
        print("Bot started. Press ctrl + c to shutdown")
        await dp.start_polling(bot)
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    asyncio.run(main())
