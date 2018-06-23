from exchange.manager.base import BaseManager
from exchange.client.binance import BinanceApiClient
from exchange.exception import ExchangeConnectionException, ExchangeNotProcessedException, \
    ExchangeNotSupportMethodException, NotValidCurrency, NotValidCurrencyPair

from decimal import Decimal
import json


class BinanceManager(BaseManager):
    def __init__(self):
        self.client = BinanceApiClient()

    def get_ticker(self, currencypair=None):
        ticker_list = []

        if currencypair is None:
            try:
                r = self.client.symbol_price_ticker()
            except Exception:
                raise ExchangeConnectionException()

            for item in r:
                dic = {
                    'symbol': item['symbol'],
                    'price': Decimal(item['price'])
                }
                ticker_list.append(dic)
        else:
            try:
                r = self.client.symbol_price_ticker(currencypair)
            except Exception:
                raise ExchangeConnectionException()

            dic = {
                'symbol': r['symbol'],
                'price': Decimal(r['price'])
            }
            ticker_list.append(dic)
        return ticker_list

    def get_balance(self, currency=None):
        try:
            r = self.client.account_information()
        except Exception:
            raise ExchangeConnectionException()
        balance_list = []
        if currency:
            for item in r['balances']:
                if item['asset'] == currency.upper():
                    balance_list.append(item)
                    break
        else:
            balance_list += r['balances']
        return balance_list

    def get_address(self, currency):
        try:
            r = self.client.deposit_address(currency)
        except Exception:
            raise ExchangeConnectionException()
        dic = {
            'currency': currency,
            'address': r['address'],
            'destination_tag': r['addressTag']
        }
        return dic

    def get_myorder(self, currencypair):
        try:
            r = self.client.open_orders(currencypair)
        except Exception:
            raise ExchangeConnectionException()
        return r

    def get_order_history(self, currencypair):
        try:
            r = self.client.all_orders(currencypair)
        except Exception:
            raise ExchangeConnectionException()
        return r

    def get_deposit_history(self, currency):
        try:
            r = self.client.deposit_history(currencypair)
        except Exception:
            raise ExchangeConnectionException()
        return r

    def get_withdrawal_history(self, currencypair):
        try:
            r = self.client.withdraw_history(currencypair)
        except Exception:
            raise ExchangeConnectionException()
        return r

    def bid(self, currencypair, amount, price):
        try:
            r = self.client.new_order(currencypair, "BUY", amount, price)
        except Exception:
            raise ExchangeConnectionException()
        return r

    def buy(self):
        raise ExchangeNotSupportMethodException()

    def ask(self, currencypair, amount, price):
        try:
            r = self.client.new_order(currencypair, "SELL", amount, price)
        except Exception:
            raise ExchangeConnectionException()
        return r

    def sell(self):
        raise ExchangeNotSupportMethodException()

    def cancel(self, uid, currencypair, otype):
        try:
            r = self.client.cancel_order(currencypair, uid)
        except Exception:
            raise ExchangeConnectionException()
        return r

    def withdrawal(self, currency, address, amount, tag):
        try:
            r = self.client.withdraw(currency, address, amount, tag)
        except Exception:
            raise ExchangeConnectionException()
        return r
