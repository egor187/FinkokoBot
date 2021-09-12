import datetime
import sqlite3
from aiogram.types import Message
import re
import os
from typing import Union, Optional
import pytz
import exceptions
from loguru import logger

from bot import aliases

OTHER_CATEGORY = "other"


con = sqlite3.connect(os.path.join("db", "finance.db"))
con.execute("PRAGMA foreign_keys = 1")  # enable FK support for sqlite engine. Need each time when you connecting to db
con.commit()


def _get_now_datetime() -> datetime.datetime:
    """Return now datetime object"""
    tz = pytz.timezone("Europe/Moscow")
    now = datetime.datetime.now(tz)
    return now


def get_now_datetime_formatted() -> str:
    """Return now datetime formatted object"""
    now = _get_now_datetime()
    fmt = "%Y-%m-%d %H:%M:%S"
    now_formatted = now.strftime(fmt)
    return now_formatted


def _get_category_name_by_alias(category_alias: str) -> str:
    """Return category name for passed category alias"""
    if category_alias not in aliases.aliases.values():
        category_name = aliases.aliases.get(category_alias)
    else:
        category_name = category_alias
    return category_name


def parse_payment_message(income_message: Message) -> Optional[tuple[int, str]]:
    """Parse message for add payment"""
    parsed_message = re.match(r"([\d ]+) (.*)", income_message.text)
    if parsed_message:
        try:
            amount = int(parsed_message.group(1))
            category = str(_get_category_name_by_alias(parsed_message.group(2).lower()))  # return category name by key=alias
            return amount, category
        except ValueError as e:
            logger.error(e)
            raise exceptions.IncorrectAmountFormatMessage
    else:
        logger.info("Incorrect message. Need in fmt '{amount} {category}'")
        raise exceptions.IncorrectMessageException


def _get_all_categories() -> list[tuple[str, str], ...]:
    """Get all categories from db"""
    cur = con.cursor()
    cur.execute("SELECT id, name FROM Category")
    result = cur.fetchall()
    return result


def get_all_categories() -> str:
    """Get all categories from db in formatted output"""
    categories = _get_all_categories()
    no_query_answer = "You haven't registered any categories yet"
    if categories:
        answer = ""
        for category in categories:
            answer += category[1] + "\n"
        return answer
    return no_query_answer


def _get_category_id_by_name(category_name: str) -> int:
    """Return category id by name"""
    cur = con.cursor()
    cur.execute(
        f"SELECT id FROM Category WHERE name='{category_name}'"
    )
    category_id = cur.fetchone()
    return int(category_id[0])


def _get_month_payments_summary_for_categories() -> list[tuple[str, str, str], ...]:
    """Retrieve summary payments and count of transaction for categories for about month"""
    now = _get_now_datetime()
    month_ago = now - datetime.timedelta(days=30)
    cur = con.cursor()
    cur.execute(f"SELECT Category.name, Sum(Payment.amount), Count(Payment.id)"
                f" from Payment LEFT JOIN Category ON Payment.category = Category.id"
                f" WHERE paid_at > '{month_ago}' GROUP BY Category.name "
                )
    result = cur.fetchall()
    return result


def get_payments_summary_for_categories_per_month() -> str:
    """Formatted summary payments about month"""
    payments_per_month = _get_month_payments_summary_for_categories()  # tuple (category name, total amount, n-trans)
    answer = "Month payments:\n\n"
    if payments_per_month:
        for payment_group in payments_per_month:
            answer += f"'{payment_group[0]}': " \
                      f"total '{payment_group[1]}'\n" \
                      f"transaction count '{payment_group[2]}'\n"
        return answer
    return "No data"


def _get_month_payments() -> Union[dict, None]:
    categories = _get_all_categories()
    result = dict()
    cur = con.cursor()
    for category in categories:
        cur.execute("SELECT amount, paid_at FROM Payment WHERE category = ?", (category[0],))
        result[category[1]] = cur.fetchall()
    if result:
        return result
    return


def get_month_payments() -> str:
    payments = _get_month_payments().items()
    if payments:
        answer = ""
        for category, payments_tuple in payments:
            answer += f"For {category} payments is: "
            for payment in payments_tuple:
                answer += f"{payment[0]} at: {payment[1]} \n"
        return answer
    return "No data"


def add_payment(income_message: Message) -> None:
    """Add payment to db"""
    now = _get_now_datetime()
    try:
        amount, category_name = parse_payment_message(income_message)
    except (exceptions.IncorrectAmountFormatMessage, exceptions.IncorrectMessageException):
        raise

    all_categories = get_all_categories()

    if category_name not in all_categories:
        category_name = OTHER_CATEGORY

    category_id = _get_category_id_by_name(category_name)
    cur = con.cursor()
    cur.execute(
        f"INSERT INTO Payment(category, amount, paid_at) VALUES ('{category_id}', '{amount}', '{now}')"
    )


def delete_last_payment() -> None:
    """Delete last added payment from db"""
    cur = con.cursor()
    cur.execute(f"DELETE FROM Payment WHERE id = (SELECT MAX(id) FROM Payment)")


def set_budget():
    pass


def update_budget():
    pass


def del_budget():
    pass


def get_weekly_summary():
    pass


def get_monthly_summary():
    pass


def get_quart_summary():
    pass


def get_half_year_summary():
    pass


def get_year_summary():
    pass


def _init_db():
    """Initializing db"""
    with open("schema.sql", "r") as file:
        sql_schema = file.read()
        with con.cursor() as cur:
            cur.executescript(sql_schema)


def _check_db():
    """Check is db plugged in. If not init db and connect"""
    cur = con.cursor()
    cur.execute("SELECT * FROM sqlite_master")
    result = cur.fetchall()
    if result:
        return
    else:
        _init_db()


_check_db()
