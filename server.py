import logging
import os

import dotenv

from aiogram import Bot, Dispatcher, executor, types

dotenv.load_dotenv(dotenv.find_dotenv())


TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

logging.basicConfig(level=logging.INFO)

bot = Bot(token=TELEGRAM_BOT_TOKEN)
dispatcher = Dispatcher(bot)


@dispatcher.message_handler(commands=["start"])
async def welcome(message: types.Message):
    await message.answer("Hi.\nI'm your fin bot!\nLet's start our budget")


if __name__ == "__main__":
    executor.start_polling(dispatcher, skip_updates=False)
