from typing import List, Tuple, AnyStr


def get_month_summary_html_format(data: List[Tuple]) -> AnyStr:
    answer = f"<b>Month payments:</b>\n\n"
    for payment_group in data:
        answer += f"<i>{payment_group[0]}:</i> " \
                  f"{payment_group[1]}, " \
                  f"transactions: {payment_group[2]}\n"
    return answer

