import sqlite3
from aiogram.types import Message
import re
import os


con = sqlite3.connect(os.path.join("db", "finance.db"))
cur = con.cursor()


def parse_message(income_message: Message):
    parsed_message = re.match(r"([\d ]+) (.*)", income_message.text)
    if not parsed_message:
        raise Exception("don't understand you")

    amount = parsed_message.group(1)
    category = parsed_message.group(2)

    return amount, category


def get_all_categories() -> str:
    cur.execute("SELECT name, is_base FROM Category;")
    result = cur.fetchall()
    no_query_answer = "You haven't registered any categories yet"
    if result:
        answer = ""
        for category in result:
            answer += category[0] + "\n"
        return answer
    return no_query_answer


def get_category(income_message: Message):
    cur.execute("SELECT name FROM Category WHERE name = ?", (income_message.text,))
    result = cur.fetchone()[0]
    no_query_answer = "You haven't registered any categories yet"
    if result:
        return str(result)
    return no_query_answer


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
