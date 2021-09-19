class IncorrectMessageException(BaseException):
    pass


class IncorrectAmountFormatMessageException(ValueError):
    pass


class DBAccessException(BaseException):
    pass


class BudgetNotSetException(BaseException):
    pass


class BudgetLimitReachedException(BaseException):
    pass
