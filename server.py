import logging
import os

import dotenv

from aiogram import Bot, Dispatcher, executor, types

import db

dotenv.load_dotenv(dotenv.find_dotenv())


TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

logging.basicConfig(level=logging.INFO)

bot = Bot(token=TELEGRAM_BOT_TOKEN)
dispatcher = Dispatcher(bot)


@dispatcher.message_handler(commands=["start"])
async def welcome(message: types.Message):
    """Send welcome message"""
    await message.answer("Hi.\nI'm your fin bot!\nLet's start our budget")


@dispatcher.message_handler(commands=["all_categories"])
async def view_all_categories(message: types.Message):
    """Retrieve all categories"""
    answer = db.get_all_categories()
    await message.answer(answer)


@dispatcher.message_handler()
async def view_all_payments(message: types.Message):
    pass


if __name__ == "__main__":
    executor.start_polling(dispatcher, skip_updates=False)
