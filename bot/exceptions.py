class IncorrectMessageException(Exception):
    pass


class IncorrectAmountFormatMessageException(ValueError):
    pass


class IncorrectAddCategoryFormatMessageException(ValueError):
    pass


class DBAccessException(Exception):
    pass


class BudgetNotSetException(Exception):
    pass


class BudgetLimitReachedException(Exception):
    pass


class CategoryAlreadyExistsException(Exception):
    pass
