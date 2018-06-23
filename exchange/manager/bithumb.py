from datetime import datetime
from django.core.cache import cache
from decimal import Decimal

from exchange import symbol, models
from exchange.client.bithumb import BithumbApiClient
from exchange.exception import ExchangeConnectionException, ExchangeNotProcessedException, \
    ExchangeNotSupportMethodException, NotValidCurrency, NotValidCurrencyPair
from exchange.manager.base import BaseManager

from exchange.models import Order, Exchange, Type
from exchange.symbol import CurrencyPair


def conv_currency_code(currency):
    return str(currency)


def conv_code_currency(code):
    return symbol.Currency(code)


def conv_market_code(currencypair):
    if currencypair.base == symbol.Currency('KRW'):
        return conv_currency_code(currencypair.counter)


def conv_code_market(code):
    return CurrencyPair(conv_code_currency(code), symbol.Currency('KRW'))


class BithumbManager(BaseManager):
    def __init__(self):
        self.thumb = BithumbApiClient()

    def get_ticker(self, currencypair=None):
        ticker_list = []

        if currencypair is None:
            try:
                r = self.thumb.public_ticker('ALL')
            except Exception:
                raise ExchangeConnectionException()

            if r['status'] == '0000':
                data = r['data']
                for key, val in data.items():
                    if key != 'date':
                        dic = {
                            'market': conv_code_market(key),
                            'close': Decimal(str(val['closing_price'])),
                            'volume': val['volume_1day']
                        }
                        ticker_list.append(dic)
            else:
                raise ExchangeNotProcessedException(r['message'])
        else:
            if not isinstance(currencypair, symbol.CurrencyPair):
                raise NotValidCurrencyPair()

            try:
                r = self.thumb.public_ticker(conv_market_code(currencypair))
            except Exception:
                raise ExchangeConnectionException()

            if r['status'] == '0000':
                data = r['data']
                dic = {
                    'market': currencypair,
                    'close': Decimal(str(data['closing_price'])),
                    'volume': data['volume_1day']
                }
                ticker_list.append(dic)
            else:
                raise ExchangeNotProcessedException(r['message'])
        return ticker_list

    def get_balance(self, currency=None):
        balance_list = []

        if currency is None or currency == symbol.Currency("KRW"):
            try:
                r = self.thumb.balance('all')
            except Exception:
                raise ExchangeConnectionException()
        else:
            if not isinstance(currency, symbol.Currency):
                raise NotValidCurrency()

            try:
                r = self.thumb.balance(conv_currency_code(currency))
            except Exception:
                raise ExchangeConnectionException()

        if r['status'] == "0000":
            data = r['data']
            if currency == symbol.Currency("KRW"):
                dic = {
                    'currency': currency,
                    'available': data['available_krw'],
                    'pending': data['in_use_krw'],
                    'total': data['total_krw']
                }
                balance_list.append(dic)
            else:
                i = 0
                for key, val in data.items():
                    if i < 4:
                        pass
                    elif i % 5 == 4:
                        total = Decimal(str(val))
                    elif i % 5 == 0:
                        pending = Decimal(str(val))
                    elif i % 5 == 1:
                        available = Decimal(str(val))
                        dic = {
                            'currency': conv_code_currency(key.split('_')[1].upper()),
                            'available': available,
                            'pending': pending,
                            'total': total
                        }
                        balance_list.append(dic)
                    i += 1
            return balance_list
        else:
            raise ExchangeNotProcessedException(r['message'])

    def get_address(self, currency):
        if not isinstance(currency, symbol.Currency):
            raise NotValidCurrency()

        try:
            r = self.thumb.wallet_address(conv_currency_code(currency))
        except Exception:
            raise ExchangeConnectionException()

        if r['status'] == "0000":
            data = r['data']
            if "&dt=" in data['wallet_address']:
                dic = {
                    'currency': currency,
                    'address': data['wallet_address'].split("&dt=")[0],
                    'destination_tag': data['wallet_address'].split("&dt=")[1]
                }
            else:
                dic = {
                    'currency': currency,
                    'address': data['wallet_address']
                }
            return dic
        else:
            raise ExchangeNotProcessedException(r['message'])

    def get_myorder(self, currencypair):
        if not isinstance(currencypair, symbol.CurrencyPair):
            raise NotValidCurrencyPair()

        order_list = []

        try:
            r = self.thumb.orders(conv_market_code(currencypair))
        except Exception:
            raise ExchangeConnectionException()

        if r['status'] == "0000":
            data = r['data']
            for d in data:
                d['order_date'] = datetime.fromtimestamp(int(d['order_date']) / 1000000)
                d['units'] = Decimal(str(d['units']))
                d['units_remaining'] = Decimal(str(d['units_remaining']))
                d['price'] = Decimal(str(d['price']))

                dic = {
                    'id': d['order_id'],
                    'market': conv_code_market(d['order_currency']),
                    'date': d['order_date'],
                    'type': d['type'],
                    'amount': d['units'],
                    'remain': d['units_remaining'],
                    'price': d['price']
                }
                order_list.append(dic)
            return order_list
        else:
            if r['message'] == "거래 진행중인 내역이 존재하지 않습니다.":
                return order_list
            else:
                raise ExchangeNotProcessedException(r['message'])

    def get_order_history(self, currencypair):
        if not isinstance(currencypair, symbol.CurrencyPair):
            raise NotValidCurrencyPair()

        history_list = []

        try:
            r = self.thumb.user_transactions(conv_market_code(currencypair))
        except Exception:
            raise ExchangeConnectionException()

        if r['status'] == "0000":
            data = r['data']
            for d in data:
                if d['search'] == '1' or d['search'] == '2':
                    if '+ ' in d['units']:
                        d['units'] = d['units'][2:]
                    elif '- ' in d['units']:
                        d['units'] = d['units'][2:]

                    if d['search'] == '1':
                        d['search'] = 'bid'
                    elif d['search'] == '2':
                        d['search'] = 'ask'

                    d['transfer_date'] = datetime.fromtimestamp(int(d['transfer_date']) / 1000000)

                    dic = {
                        'market': currencypair,
                        'type': d['search'],
                        'date': d['transfer_date'],
                        'amount': Decimal(str(d['units'])),
                        'price': Decimal(str(d[conv_market_code(currencypair).lower() + '1krw']))
                    }
                    history_list.append(dic)
            return history_list
        else:
            raise ExchangeNotProcessedException(r['message'])

    def get_deposit_history(self, currency):
        if not isinstance(currency, symbol.Currency):
            raise NotValidCurrencyPair()

        history_list = []

        try:
            r = self.thumb.user_transactions(conv_currency_code(currency))
        except Exception:
            raise ExchangeConnectionException()

        if r['status'] == "0000":
            data = r['data']
            for d in data:
                if d['search'] == '4':
                    if "+ " in d['units']:
                        d['units'] = d['units'][2:]

                    dic = {
                        'currency': currency,
                        'date': datetime.fromtimestamp(int(d['transfer_date']) / 1000000),
                        'amount': Decimal(str(d['units']))
                    }
                    history_list.append(dic)
            return history_list
        else:
            raise ExchangeNotProcessedException(r['message'])

    def get_withdrawal_history(self, currency):
        if not isinstance(currency, symbol.Currency):
            raise NotValidCurrencyPair()

        history_list = []

        try:
            r = self.thumb.user_transactions(conv_currency_code(currency))
        except Exception:
            raise ExchangeConnectionException()

        if r['status'] == "0000":
            data = r['data']
            for d in data:
                if d['search'] == '5':
                    if "- " in d['units']:
                        d['units'] = d['units'][2:]
                    dic = {
                        'currency': currency,
                        'date': datetime.fromtimestamp(int(d['transfer_date']) / 1000000),
                        'amount': Decimal(str(d['units']))
                    }
                    history_list.append(dic)
            return history_list
        else:
            raise ExchangeNotProcessedException(r['message'])

    def bid(self, currencypair, amount, price):
        if not isinstance(currencypair, symbol.CurrencyPair):
            raise NotValidCurrencyPair()

        try:
            r = self.thumb.place(conv_market_code(currencypair), amount, price, "bid")
        except Exception:
            raise ExchangeConnectionException()

        if r['status'] == "0000":
            order_id = r['order_id']

            # TODO Add Extra Properties...
            exchange = Exchange.objects.get(pk=1)
            type = Type.objects.get(pk=1)
            counter = models.Currency.objects.filter(symbol=str(currencypair.counter)).get()
            base = models.Currency.objects.filter(symbol=str(currencypair.base)).get()
            Order(exchange=exchange, counter=counter.id, base=base.id, euid=order_id, type=type,
                  amount=amount, price=price, total=amount * price, src_btc_price=0, src2btc=0, dest_price=0).save()

            orderbook = cache.get("bithumb")
            if orderbook is None:
                order_list = []
                dic = {"currencypair": currencypair, "type": "bid", "amount": amount, "price": price,
                       "total": amount * price, "order_id": order_id, "registered_time": str(datetime.now())[:19]}
                order_list.append(dic)
                cache.set("bithumb", order_list, timeout=None)

            else:
                dic = {"currencypair": currencypair, "type": "bid", "amount": amount, "price": price,
                       "total": amount * price, "order_id": order_id, "registered_time": str(datetime.now())[:19]}
                orderbook.append(dic)
                cache.set("bithumb", orderbook, timeout=None)

            return order_id
        else:
            raise ExchangeNotProcessedException(r['message'])

    def buy(self):
        raise ExchangeNotSupportMethodException()

    def ask(self, currencypair, amount, price):
        if not isinstance(currencypair, symbol.CurrencyPair):
            raise NotValidCurrencyPair()

        try:
            r = self.thumb.place(conv_market_code(currencypair), amount, price, "ask")
        except Exception:
            raise ExchangeConnectionException()

        if r['status'] == "0000":
            order_id = r['order_id']

            # TODO Add Extra Properties...
            exchange = Exchange.objects.get(pk=1)
            type = Type.objects.get(pk=2)
            counter = models.Currency.objects.filter(symbol=str(currencypair.counter)).get()
            base = models.Currency.objects.filter(symbol=str(currencypair.base)).get()
            Order(exchange=exchange, counter=counter.id, base=base.id, euid=order_id, type=type,
                  amount=amount, price=price, total=amount * price, src_btc_price=0, src2btc=0, dest_price=0).save()

            orderbook = cache.get("bithumb")
            if orderbook is None:
                order_list = []
                dic = {"currencypair": currencypair, "type": "ask", "amount": amount, "price": price,
                       "total": amount * price, "order_id": order_id, "registered_time": str(datetime.now())[:19]}
                order_list.append(dic)
                cache.set("bithumb", order_list, timeout=None)

            else:
                dic = {"currencypair": currencypair, "type": "ask", "amount": amount, "price": price,
                       "total": amount * price, "order_id": order_id, "registered_time": str(datetime.now())[:19]}
                orderbook.append(dic)
                cache.set("bithumb", orderbook, timeout=None)

            return order_id
        else:
            raise ExchangeNotProcessedException(r['message'])

    def sell(self):
        raise ExchangeNotSupportMethodException()

    def cancel(self, uid, currencypair, otype):
        if not isinstance(currencypair, symbol.CurrencyPair):
            raise NotValidCurrencyPair()

        try:
            r = self.thumb.cancel(otype, uid, conv_market_code(currencypair))
        except Exception:
            raise ExchangeConnectionException()

        if r['status'] == "0000":
            orderbook = cache.get("bithumb")
            if orderbook is not None:
                for i in range(len(orderbook)):
                    if orderbook[i]["order_id"] == uid:
                        del orderbook[i]
                        break
            return True
        else:
            raise ExchangeNotProcessedException(r['message'])

    def withdrawal(self, currency, address, amount, tag=None):
        if not isinstance(currency, symbol.Currency):
            raise NotValidCurrencyPair()

        try:
            r = self.thumb.btc_withdrawal(conv_currency_code(currency), address, amount, tag)
        except Exception:
            raise ExchangeConnectionException()

        if r['status'] == "0000":
            return True
        else:
            raise ExchangeNotProcessedException(r['message'])
