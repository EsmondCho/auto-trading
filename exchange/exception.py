class BaseExchangeException(Exception):
    """Base class for exceptions in this module."""
    pass


class ExchangeConnectionException(BaseExchangeException):
    """Exception raised in the connectino error."""


class ExchangeNotProcessedException(BaseExchangeException):
    """Exception raised in the not processing error."""

    def __init__(self, message):
        self.message = message


class ExchangeNotSupportMethodException(BaseExchangeException):
    """Exception raised in the using not support method."""


class ExchangeNotSupportCurrency(BaseExchangeException):
    """Exception raised in the using not support currency"""


class NotValidCurrencyPair(BaseExchangeException):
    """Exception raised in the using not instanceof CurrencyPair"""


class NotValidCurrency(BaseExchangeException):
    """Exception raised in the using not instanceof Currency"""
