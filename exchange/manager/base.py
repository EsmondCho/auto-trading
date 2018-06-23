from abc import *


class BaseManager(metaclass=ABCMeta):
    @abstractmethod
    def get_ticker(self, market):
        pass

    @abstractmethod
    def get_balance(self, currency):
        pass

    @abstractmethod
    def get_address(self, currency):
        pass

    @abstractmethod
    def get_myorder(self, market):
        pass

    @abstractmethod
    def get_order_history(self, market):
        pass

    @abstractmethod
    def get_deposit_history(self, currency):
        pass

    @abstractmethod
    def get_withdrawal_history(self, currency):
        pass

    @abstractmethod
    def bid(self, market, amount, price):
        pass

    @abstractmethod
    def buy(self):
        pass

    @abstractmethod
    def ask(self, market, amount, price):
        pass

    @abstractmethod
    def sell(self):
        pass

    @abstractmethod
    def cancel(self, uid, market, otype):
        pass

    @abstractmethod
    def withdrawal(self, currency, address, amount, tag):
        pass
