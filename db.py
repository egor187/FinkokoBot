import datetime
import sqlite3
from aiogram.types import Message
import re
import os
from typing import Union
import pytz


con = sqlite3.connect(os.path.join("db", "finance.db"))
cur = con.cursor()


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


def parse_message(income_message: Message):
    """Parse message for add payment"""
    parsed_message = re.match(r"([\d ]+) (.*)", income_message.text)
    if not parsed_message:
        raise Exception("don't understand you")

    amount = parsed_message.group(1)
    category = parsed_message.group(2)

    return amount, category


def _get_all_categories() -> list[tuple[str, str], ...]:
    """Get all categories from db"""
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


def _get_month_payments_summary_for_categories() -> list[tuple[str, str, str], ...]:
    """Retrieve summary payments and count of transaction for categories for about month"""
    now = _get_now_datetime()
    month_ago = now - datetime.timedelta(days=30)
    cur.execute(f"SELECT Category.name, Sum(Payment.amount), Count(Payment.id)" 
                f" from Payment LEFT JOIN Category ON Payment.category = Category.id"
                f" WHERE paid_at > '{month_ago}' GROUP BY Category.name "
                )
    result = cur.fetchall()
    return result


def get_payments_summary_for_categories_per_month() -> str:
    """Formatted summary payments about month"""
    payments_per_month = _get_month_payments_summary_for_categories()  # tuple (category name, total amount, n-trans)
    answer = ""
    if payments_per_month:
        for payment_group in payments_per_month:
            answer += f"For category {payment_group[0]} " \
                      f"month summary is: '{payment_group[1]}'" \
                      f" payments count: {payment_group[2]}\n"
        return answer
    return "No data"


def _get_month_payments() -> Union[dict, None]:
    categories = _get_all_categories()
    result = dict()
    for category in categories:
        # TODO refactor to .executemany with iterable categories
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


def add_payment():
    pass


def del_last_payment():
    pass


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
        cur.executescript(sql_schema)


def _check_db():
    """Check is db plugged in. If not init db and connect"""
    cur.execute("SELECT * FROM sqlite_master")
    result = cur.fetchall()
    if result:
        return
    else:
        _init_db()


_check_db()
