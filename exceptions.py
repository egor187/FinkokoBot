class IncorrectMessageException(BaseException):
    pass


class IncorrectAmountFormatMessage(ValueError):
    pass


class DBAccessError(BaseException):
    pass
