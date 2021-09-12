from loguru import logger
import os

import dotenv

from aiogram import Bot, Dispatcher, executor, types

# import db
from bot import exceptions, pg_db as db

dotenv.load_dotenv(dotenv.find_dotenv())


TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

# webhook settings
WEBHOOK_HOST = os.getenv("WEBHOOK_HOST")
WEBHOOK_PATH = f'/webhook/{TELEGRAM_BOT_TOKEN}'
WEBHOOK_URL = f'{WEBHOOK_HOST}{WEBHOOK_PATH}'
WEBAPP_HOST = os.getenv("WEBAPP_HOST")
WEBAPP_PORT = int(os.getenv("PORT", 5000))


bot = Bot(token=TELEGRAM_BOT_TOKEN)
dispatcher = Dispatcher(bot)


async def on_startup(dp: Dispatcher) -> None:
    await bot.set_webhook(url=f"{WEBHOOK_HOST}{WEBHOOK_PATH}")


@dispatcher.message_handler(commands=["start"])
async def welcome(message: types.Message):
    """Send welcome message"""
    await message.answer("Hi.\nI'm your fin bot!\nLet's start our budget")


@dispatcher.message_handler(commands=["all_categories"])
async def view_all_categories(message: types.Message):
    """Send message with all categories to user"""
    answer = db.get_all_categories()
    await message.answer(answer)


@dispatcher.message_handler(commands=["month"])
async def view_month_payments(message: types.Message):
    """Send message with all payments in last month"""
    result = db.get_payments_summary_for_categories_per_month()
    await message.answer(result, parse_mode="HTML")


@dispatcher.message_handler(commands=["month_detail"])
async def view_month_payments(message: types.Message):
    """Send message with all payments in last month"""
    result = db.get_month_payments()
    await message.answer(result, parse_mode="HTML")


@dispatcher.message_handler(commands=["del"])
async def delete_last_payment(message: types.Message):
    try:
        db.delete_last_payment()
    except Exception as e:
        logger.error(e)
        await message.answer("Something wrong with dbaccess")
    else:
        await message.answer("Last payment deleted")


@dispatcher.message_handler()
async def add_payment_view(message: types.Message):
    """Entrypoint to 'add_payment' process"""
    try:
        db.add_payment(message)
    except (exceptions.IncorrectAmountFormatMessage, exceptions.IncorrectMessageException):
        await message.answer("Incorrect message. Need in fmt '{amount} {category}'")
    else:
        await message.answer("Payment added")


@dispatcher.message_handler(commands=["show"])
async def detail_handler(message: types.Message):
    """Init dialog with summary details"""
    pass


if __name__ == "__main__":
    # executor.start_polling(dispatcher, skip_updates=False)
    executor.start_webhook(
        dispatcher=dispatcher,
        webhook_path=WEBHOOK_PATH,
        on_startup=on_startup,
        skip_updates=False,
        host=WEBAPP_HOST,
        port=WEBAPP_PORT,
    )
