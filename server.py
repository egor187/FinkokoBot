import logging
import os

import dotenv

from aiogram import Bot, Dispatcher, executor, types

import db
import exceptions

dotenv.load_dotenv(dotenv.find_dotenv())


TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")


bot = Bot(token=TELEGRAM_BOT_TOKEN)
dispatcher = Dispatcher(bot)


@dispatcher.message_handler(commands=["start"])
async def welcome(message: types.Message):
    """Send welcome message"""
    await message.answer("Hi.\nI'm your fin bot!\nLet's start our budget")


@dispatcher.message_handler(commands=["all_categories"])
async def view_all_categories(message: types.Message):
    """Send message with all categories to user"""
    answer = db.get_all_categories()
    await message.answer(answer)


@dispatcher.message_handler(commands=["payments"])
async def view_month_payments(message: types.Message):
    """Send message with all payments in last month"""
    result = db.get_payments_summary_for_categories_per_month()
    await message.answer(result)


@dispatcher.message_handler()
async def add_payment_view(message: types.Message):
    """Entrypoint to 'add_payment' process"""
    try:
        db.add_payment(message)
    except (exceptions.IncorrectAmountFormatMessage, exceptions.IncorrectMessageException):
        await message.answer("Incorrect message. Need in fmt '{amount} {category}'")
    else:
        await message.answer("Payment added")


# TODO README.md


if __name__ == "__main__":
    executor.start_polling(dispatcher, skip_updates=False)
