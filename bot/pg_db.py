import datetime
import dotenv
import psycopg2
from aiogram.types import Message
import re
import os
from typing import Union, Optional
import pytz
import exceptions
from loguru import logger

import aliases

from formatters import get_month_summary_html_format, get_payments_details_per_month_html_format


OTHER_CATEGORY = "other"

dotenv.load_dotenv(dotenv.find_dotenv())
SQL_SCHEMA = open("bot/pg_schema.sql", mode="r")


connection = psycopg2.connect(
    dbname=os.getenv("DB_NAME_PROD"),
    user=os.getenv("DB_USER_PROD"),
    password=os.getenv("DB_PASSWORD_PROD"),
    sslmode='require',
    host=os.getenv("DB_HOST_PROD"))

connection.autocommit = True


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
            logger.info(e)
            raise exceptions.IncorrectAmountFormatMessage
    else:
        logger.error("Incorrect message. Need in fmt '{amount} {category}'")
        raise exceptions.IncorrectMessageException


def _get_all_categories() -> list[tuple[str, str], ...]:
    """Get all categories from db"""
    with connection.cursor() as cur:
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
    with connection.cursor() as cur:
        cur.execute(
            f"SELECT id FROM Category WHERE name='{category_name}'"
        )
        category_id = cur.fetchone()
    return int(category_id[0])


def _get_month_payments_summary_for_categories() -> list[tuple[str, str, str], ...]:
    """Retrieve summary payments and count of transaction for categories for about month"""
    now = _get_now_datetime()
    month_ago = now - datetime.timedelta(days=30)
    with connection.cursor() as cur:
        cur.execute(f"SELECT Category.name, Sum(Payment.amount), Count(Payment.id)" 
                    f" from Payment LEFT JOIN Category ON Payment.category = Category.id"
                    f" WHERE paid_at > '{month_ago}' GROUP BY Category.name "
                    )
        result = cur.fetchall()
    return result


def get_payments_summary_for_categories_per_month() -> str:
    """Formatted summary payments about month"""
    payments_per_month = _get_month_payments_summary_for_categories()  # tuple (category name, total amount, n-trans)
    if payments_per_month:
        answer = get_month_summary_html_format(payments_per_month)
        return answer
    return "No data"


def _get_month_payments() -> Union[dict, None]:
    categories = _get_all_categories()
    result = dict()
    with connection.cursor() as cur:
        for category in categories:
            cur.execute(f"SELECT amount, paid_at FROM Payment WHERE category = {category[0]}")
            query_result = cur.fetchall()
            if len(query_result) > 0:
                result[category[1]] = query_result
    if result:
        return result
    return


def get_month_payments() -> str:
    payments = _get_month_payments().items()
    if payments:
        answer = get_payments_details_per_month_html_format(payments)
        return answer
    return "No data"


def add_payment(income_message: Message) -> None:
    """Add payment to db"""
    now = _get_now_datetime()
    try:
        amount, category_name = parse_payment_message(income_message)
    except (exceptions.IncorrectAmountFormatMessageException, exceptions.IncorrectMessageException):
        raise

    all_categories = get_all_categories()

    if category_name not in all_categories:
        category_name = OTHER_CATEGORY

    category_id = _get_category_id_by_name(category_name)

    budget = _get_last_active_budget()

    with connection.cursor() as cur:
        cur.execute(
            f"INSERT INTO Payment(category, amount, paid_at) VALUES ('{category_id}', '{amount}', '{now}')"
        )

    if budget:
        with connection.cursor() as cur:
            cur.execute(
                f"UPDATE Budget SET balance = balance - {amount} WHERE id = {budget.get('id')}"
            )

        if budget.get("balance") < amount:
            raise exceptions.BudgetLimitReachedException


def delete_last_payment() -> None:
    """Delete last added payment from db"""
    with connection.cursor() as cur:
        cur.execute(f"DELETE FROM Payment WHERE id = (SELECT MAX(id) FROM Payment)")


def parse_detail_message(income_message: Message):
    pass


def get_category_summary(income_message: Message) -> None:
    """Get summary payments for category"""
    try:
        amount, category_name = parse_detail_message(income_message)
    except (exceptions.IncorrectAmountFormatMessageException, exceptions.IncorrectMessageException):
        raise


def set_budget(month_limit: str) -> None:
    """Set month budget"""
    created_at = _get_now_datetime()
    expired_at = created_at + datetime.timedelta(days=30)

    try:
        month_limit = int(month_limit)
    except ValueError:
        raise
    with connection.cursor() as cur:
        cur.execute(
            f"INSERT INTO Budget(month_limit, created_at, expired_at, balance) VALUES ('{month_limit}', '{created_at}', '{expired_at}', '{month_limit}')"
        )


def update_budget():
    pass


def _get_last_active_budget():
    """Возвращает поля последнего действующего бюджета """
    with connection.cursor() as cur:
        cur.execute(
            f"SELECT * FROM Budget "
            f"WHERE CURRENT_TIMESTAMP BETWEEN created_at AND expired_at "
            f"ORDER BY created_at DESC LIMIT 1"
        )
        budget = cur.fetchone()
    if budget:
        result = {
            "id": budget[0],
            "month_limit": budget[1],
            "created_at": budget[2],
            "expired_at": budget[3],
            "balance": budget[4]
        }
        return result
    return None


# deprecated realization with calculation result at time
# def get_balance():
#     try:
#         with connection.cursor() as cur:
#             cur.execute("select b.month_limit - Sum(amount) from Payment as p, Budget as b where "
#                         "p.paid_at between (select created_at from Budget ORDER BY created_at DESC LIMIT 1) "
#                         "AND (select expired_at from Budget ORDER BY expired_at DESC LIMIT 1) GROUP BY b.id;")
#             balance = cur.fetchone()[0]
#     except TypeError:
#         raise exceptions.BudgetNotSetException
#     except Exception:
#         raise exceptions.DBAccessException
#     else:
#         return balance

def get_balance():
    try:
        with connection.cursor() as cur:
            cur.execute("SELECT balance FROM Budget "
                        "WHERE CURRENT_TIMESTAMP BETWEEN created_at AND expired_at "
                        "ORDER BY created_at DESC LIMIT 1")
            balance = cur.fetchone()[0]
    except TypeError:
        raise exceptions.BudgetNotSetException
    except Exception:
        raise exceptions.DBAccessException
    else:
        return balance


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


def _init_db(sql_file):
    """Initializing db"""
    with connection.cursor() as cur:
        cur.execute(sql_file.read())


def _check_db():
    """Check is db plugged in. If not init db and connect"""
    with connection.cursor() as cur:
        try:
            cur.execute("SELECT * FROM Category")
            result = cur.fetchone()
            return
        except Exception:
            _init_db(SQL_SCHEMA)


_check_db()
