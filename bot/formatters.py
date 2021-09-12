from typing import List, Tuple, AnyStr, ItemsView
from datetime import date


def get_month_summary_html_format(data: List[Tuple[AnyStr, date]]) -> AnyStr:
    answer = f"<b>Month payments:</b>\n\n"
    for payment_group in data:
        answer += f"<i>{payment_group[0]}:</i> " \
                  f"{payment_group[1]}, " \
                  f"transactions: {payment_group[2]}\n"
    return answer


def get_payments_details_per_month_html_format(data: ItemsView[AnyStr, List[Tuple]]) -> AnyStr:
    answer = f"<b>For last month you hot next payments:</b>\n\n"
    for category, payments_info in data:
        answer += f"<i>{category}</i>:\n"
        for payment in payments_info:
            answer += f"amount: {payment[0]} at: {payment[1].strftime('%Y/%m/%d')}\n"
        answer += "\n"
    return answer

