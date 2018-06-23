from datetime import datetime, timezone
import pytz

from django.core.cache import cache
from decimal import Decimal

from exchange import symbol, models
from exchange.client.bittrex import BittrexApiClient
from exchange.symbol import CurrencyPair
from exchange.exception import ExchangeConnectionException, ExchangeNotProcessedException, \
    ExchangeNotSupportMethodException, NotValidCurrencyPair, NotValidCurrency
from exchange.manager.base import BaseManager
from exchange.models import Order, Exchange, Type

commonCurrencies = {
    'BCC': 'BCH',
    '': 'BCC',
}


def conv_currency_code(currency):
    r = str(currency)

    for c in commonCurrencies:
        if r == commonCurrencies[c]:
            r = c
            break

    return r


def conv_code_currency(code):
    if code in commonCurrencies:
        return commonCurrencies[code]
    else:
        return symbol.Currency(code)


def conv_market_code(currencypair):
    return conv_currency_code(currencypair.base) + '-' + conv_currency_code(currencypair.counter)


def conv_code_market(code):
    cm = code.split('-')
    counter = cm[1]
    base = cm[0]
    return CurrencyPair(conv_code_currency(counter), symbol.Currency(base))


class BittrexManager(BaseManager):
    def __init__(self):
        self.apiclient = BittrexApiClient()

    def get_ticker(self, currencypair=None):
        result = []

        try:
            r = self.apiclient.getmarketsummaries()
        except Exception:
            raise ExchangeConnectionException()

        if r['success'] is True:
            data = r['result']
            if currencypair is None:
                for d in data:
                    fm = {'market': conv_code_market(d['MarketName']),
                          'close': Decimal(str(d['Last'])),
                          'volume': d['Volume']}
                    result.append(fm)
            else:
                if not isinstance(currencypair, symbol.CurrencyPair):
                    raise NotValidCurrencyPair()

                market = conv_market_code(currencypair)

                for d in data:
                    if d['MarketName'] == market:
                        fm = {'market': currencypair,
                              'close': Decimal(str(d['Last'])),
                              'volume': d['Volume']}
                        result.append(fm)

            return result
        else:
            raise ExchangeNotProcessedException(r['message'])

    def get_balance(self, currency=None):
        result = []

        if currency is None:
            try:
                r = self.apiclient.getbalances()
            except Exception:
                raise ExchangeConnectionException()

            if r['success'] is True:
                data = r['result']
                for d in data:
                    fm = {'currency': conv_code_currency(d['Currency']),
                          'available': Decimal(str(d['Available'])),
                          'pending': Decimal(str(d['Pending'])),
                          'total': Decimal(str(d['Balance']))}
                    result.append(fm)
            else:
                raise ExchangeNotProcessedException(r['message'])
        else:
            if not isinstance(currency, symbol.Currency):
                raise NotValidCurrency()

            try:
                r = self.apiclient.getbalance(conv_currency_code(currency))
            except Exception:
                raise ExchangeConnectionException()

            if r['success'] is True:
                data = r['result']
                fm = {'currency': conv_code_currency(data['Currency']),
                      'available': Decimal(str(data['Available'])),
                      'pending': Decimal(str(data['Pending'])),
                      'total': Decimal(str(data['Balance']))}
                result.append(fm)
            else:
                raise ExchangeNotProcessedException(r['message'])
        return result

    def get_address(self, currency):
        if not isinstance(currency, symbol.Currency):
            raise NotValidCurrency()

        try:
            r = self.apiclient.getdepositaddress(currency)
        except Exception:
            raise ExchangeConnectionException()

        if r['success'] is True:
            data = r['result']
            fm = {'currency': currency, 'address': data['Address']}
            return fm
        else:
            raise ExchangeNotProcessedException(r['message'])

    def get_myorder(self, currencypair=None):
        if not isinstance(currencypair, symbol.CurrencyPair):
            raise NotValidCurrencyPair()

        result = []

        try:
            r = self.apiclient.getopenorders(conv_market_code(currencypair))
        except Exception:
            raise ExchangeConnectionException()

        if r['success'] is True:
            data = r['result']
            for d in data:
                if d['OrderType'] == 'LIMIT_BUY':
                    d['OrderType'] = 'bid'
                elif d['OrderType'] == 'LIMIT_SELL':
                    d['OrderType'] = 'ask'

                try:
                    d['Opened'] = datetime.strptime(d['Opened'], '%Y-%m-%dT%H:%M:%S.%f')\
                        .replace(tzinfo=timezone.utc).astimezone(tz=pytz.timezone('Asia/Seoul')).replace(tzinfo=None)
                except ValueError:
                    d['Opened'] = datetime.strptime(d['Opened'], '%Y-%m-%dT%H:%M:%S') \
                        .replace(tzinfo=timezone.utc).astimezone(tz=pytz.timezone('Asia/Seoul')).replace(tzinfo=None)

                fm = {'id': d['OrderUuid'],
                      'market': currencypair,
                      'date': d['Opened'],
                      'type': d['OrderType'],
                      'amount': Decimal(str(d['Quantity'])),
                      'remain': Decimal(str(d['QuantityRemaining'])),
                      'price': Decimal(str(d['Limit']))}
                result.append(fm)
            return result
        else:
            raise ExchangeNotProcessedException(r['message'])

    def get_order_history(self, currencypair):
        if not isinstance(currencypair, symbol.CurrencyPair):
            raise NotValidCurrencyPair()

        result = []

        try:
            r = self.apiclient.getorderhistory(conv_market_code(currencypair), 10)
        except Exception:
            raise ExchangeConnectionException()

        if r['success'] is True:
            data = r['result']
            for d in data:
                if d['OrderType'] == 'LIMIT_BUY':
                    d['OrderType'] = 'bid'
                elif d['OrderType'] == 'LIMIT_SELL':
                    d['OrderType'] = 'ask'

                try:
                    d['TimeStamp'] = datetime.strptime(d['TimeStamp'], '%Y-%m-%dT%H:%M:%S.%f')\
                        .replace(tzinfo=timezone.utc).astimezone(tz=pytz.timezone('Asia/Seoul')).replace(tzinfo=None)
                except ValueError:
                    d['TimeStamp'] = datetime.strptime(d['TimeStamp'], '%Y-%m-%dT%H:%M:%S') \
                        .replace(tzinfo=timezone.utc).astimezone(tz=pytz.timezone('Asia/Seoul')).replace(tzinfo=None)

                fm = {'market': d['Exchange'],
                      'type': d['OrderType'],
                      'date': d['TimeStamp'],
                      'amount': Decimal(str(d['Quantity'])),
                      'price': Decimal(str(d['Limit']))}
                result.append(fm)
            return result
        else:
            raise ExchangeNotProcessedException(r['message'])

    def get_deposit_history(self, currency):
        if not isinstance(currency, symbol.Currency):
            raise NotValidCurrency()

        result = []

        try:
            r = self.apiclient.getdeposithistory(conv_currency_code(currency), 10)
        except Exception:
            raise ExchangeConnectionException()

        if r['success'] is True:
            data = r['result']
            for d in data:
                try:
                    d['LastUpdated'] = datetime.strptime(d['LastUpdated'], '%Y-%m-%dT%H:%M:%S.%f')\
                        .replace(tzinfo=timezone.utc).astimezone(tz=pytz.timezone('Asia/Seoul')).replace(tzinfo=None)
                except ValueError:
                    d['LastUpdated'] = datetime.strptime(d['LastUpdated'], '%Y-%m-%dT%H:%M:%S') \
                        .replace(tzinfo=timezone.utc).astimezone(tz=pytz.timezone('Asia/Seoul')).replace(tzinfo=None)
                fm = {'currency': currency,
                      'date': d['LastUpdated'],
                      'amount': Decimal(str(d['Amount']))}
                result.append(fm)
            return result
        else:
            raise ExchangeNotProcessedException(r['message'])

    def get_withdrawal_history(self, currency):
        if not isinstance(currency, symbol.Currency):
            raise NotValidCurrency()

        result = []

        try:
            r = self.apiclient.getwithdrawalhistory(currency, 10)
        except Exception:
            raise ExchangeConnectionException()

        if r['success'] is True:
            data = r['result']
            for d in data:
                try:
                    d['Opened'] = datetime.strptime(d['Opened'], '%Y-%m-%dT%H:%M:%S.%f')\
                        .replace(tzinfo=timezone.utc).astimezone(tz=pytz.timezone('Asia/Seoul')).replace(tzinfo=None)
                except ValueError:
                    d['Opened'] = datetime.strptime(d['Opened'], '%Y-%m-%dT%H:%M:%S') \
                        .replace(tzinfo=timezone.utc).astimezone(tz=pytz.timezone('Asia/Seoul')).replace(tzinfo=None)
                fm = {'currency': currency,
                      'date': d['Opened'],
                      'amount': Decimal(str(d['Amount']))}
                result.append(fm)
            return result
        else:
            raise ExchangeNotProcessedException(r['message'])

    def bid(self, currencypair, amount, price):
        if not isinstance(currencypair, symbol.CurrencyPair):
            raise NotValidCurrencyPair()

        try:
            r = self.apiclient.buylimit(conv_market_code(currencypair), amount, price)
        except Exception:
            raise ExchangeConnectionException()

        if r['success'] is True:
            uuid = r['result']['uuid']

            # TODO Add Extra Properties...
            exchange = Exchange.objects.get(pk=2)
            type = Type.objects.get(pk=1)
            counter = models.Currency.objects.filter(symbol=str(currencypair.counter)).get()
            base = models.Currency.objects.filter(symbol=str(currencypair.base)).get()
            Order(exchange=exchange, counter=counter.id, base=base.id, euid=uuid, type=type,
                  amount=amount, price=price, total=amount * price, src_btc_price=0, src2btc=0, dest_price=0).save()

            orderbook = cache.get("bittrex")
            if orderbook is None:
                order_list = []
                dic = {"currencypair": currencypair, "type": "bid", "amount": amount, "price": price,
                       "total": amount * price, "order_id": uuid, "registered_time": str(datetime.now())[:19]}
                order_list.append(dic)
                cache.set("bittrex", order_list, timeout=None)

            else:
                dic = {"currencypair": currencypair, "type": "bid", "amount": amount, "price": price,
                       "total": amount * price, "order_id": uuid, "registered_time": str(datetime.now())[:19]}
                orderbook.append(dic)
                cache.set("bittrex", orderbook, timeout=None)

            return uuid
        else:
            raise ExchangeNotProcessedException(r['message'])

    def buy(self):
        raise ExchangeNotSupportMethodException()

    def ask(self, currencypair, amount, price):
        if not isinstance(currencypair, symbol.CurrencyPair):
            raise NotValidCurrencyPair()

        try:
            r = self.apiclient.selllimit(conv_market_code(currencypair), amount, price)
        except Exception:
            raise ExchangeConnectionException()

        if r['success'] is True:
            uuid = r['result']['uuid']

            # TODO Add Extra Properties...
            exchange = Exchange.objects.get(pk=2)
            type = Type.objects.get(pk=2)
            counter = models.Currency.objects.filter(symbol=str(currencypair.counter)).get()
            base = models.Currency.objects.filter(symbol=str(currencypair.base)).get()
            Order(exchange=exchange, counter=counter.id, base=base.id, euid=uuid, type=type,
                  amount=amount, price=price, total=amount * price, src_btc_price=0, src2btc=0, dest_price=0).save()

            orderbook = cache.get("bittrex")
            if orderbook is None:
                order_list = []
                dic = {"currencypair": currencypair, "type": "ask", "amount": amount, "price": price,
                       "total": amount * price, "order_id": uuid, "registered_time": str(datetime.now())[:19]}
                order_list.append(dic)
                cache.set("bittrex", order_list, timeout=None)

            else:
                dic = {"currencypair": currencypair, "type": "ask", "amount": amount, "price": price,
                       "total": amount * price, "order_id": uuid, "registered_time": str(datetime.now())[:19]}
                orderbook.append(dic)
                cache.set("bittrex", orderbook, timeout=None)

            return uuid
        else:
            raise ExchangeNotProcessedException(r['message'])

    def sell(self):
        raise ExchangeNotSupportMethodException()

    def cancel(self, uid, currencypair=None, otype=None):
        try:
            r = self.apiclient.cancel(uid)
        except Exception:
            raise ExchangeConnectionException()

        if r['success'] is True:
            orderbook = cache.get("bittrex")
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
            raise NotValidCurrency()

        try:
            r = self.apiclient.withdraw(conv_currency_code(currency), address, amount, tag)
        except Exception:
            raise ExchangeConnectionException()

        if r['success'] is True:
            return True
        else:
            raise ExchangeNotProcessedException(r['message'])
