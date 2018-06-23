import math
import base64
from urllib.parse import urlencode
import json
import time
import hmac
import hashlib
import deprecation
import requests
from dynamic_preferences.registries import global_preferences_registry

global_preferences = global_preferences_registry.manager()


class BithumbApiClient:

    def __init__(self):
        self.public = ['ticker', 'orderbook', 'recent_transactions']
        self.info = ['account', 'balance', 'wallet_address', 'ticker', 'orders', 'user_transactions']
        self.trade = ['place', 'order_detail', 'cancel', 'btc_withdrawal', 'krw_deposit', 'krw_withdrawal',
                      'market_buy', 'market_sell']

    def microtime(self, get_as_float=False):
        if get_as_float:
            return time.time()
        else:
            return '%f %d' % math.modf(time.time())

    def usectime(self):
        mt = self.microtime(False)
        mt_array = mt.split(" ")[:2]
        return mt_array[1] + mt_array[0][2:5]

    def query(self, type, method, query={}):
        host = "api.bithumb.com"
        endpoint = '/public/'
        if type == "public":
            endpoint += method + '/' + query['currency']
            headers = {}
            body = None
            method = "GET"
        else:
            if method in self.info:
                endpoint = '/info/' + method
            elif method in self.trade:
                endpoint = '/trade/' + method

            endpoint_item_array = {
                "endpoint": endpoint
            }

            body = urlencode(dict(endpoint_item_array, **query))
            nonce = self.usectime()
            auth = endpoint + '\0' + body + '\0' + nonce
            signature = hmac.new(bytes(global_preferences['exchange_bithumbApiSecret'].encode('utf-8')), auth.encode('utf-8'), hashlib.sha512).hexdigest()
            signature64 = base64.b64encode(signature.encode('utf-8')).decode('utf-8')
            headers = {
                'Accept': 'application/json',
                'Content-Type': 'application/x-www-form-urlencoded',
                'Api-Key': global_preferences['exchange_bithumbApiKey'],
                'Api-Sign': str(signature64),
                'Api-Nonce': nonce,
            }
            method = "POST"

        if method == "POST":
            r = requests.post("https://" + host + endpoint, headers=headers, data=body)
        else:
            r = requests.get("https://" + host + endpoint)
        response = json.loads(r.text) #conn.getresponse().read()

        return response

    def public_ticker(self, currency):
        return self.query('public', 'ticker/', {'currency': currency})

    def orderbook(self, currency, group_orders=1, count=5):
        return self.query('public', 'orderbook', {'currency': currency, 'group_orders': group_orders, 'count': count})

    def recent_transactions(self, currency, offset=0, count=20):
        return self.query('public', 'return_transactions', {'currency': currency, 'offset': offset, 'count': count})

    def account(self, currency):
        return self.query('private', 'account', {'currency': currency})

    def balance(self, currency):
        return self.query('private', 'balance', {'currency': currency})

    def wallet_address(self, currency):
        return self.query('private', 'wallet_address', {'currency': currency})

    def info_ticker(self, order_currency, payment_currency):
        return self.query('private', 'ticker', {'order_currency': order_currency, 'payment_currency': payment_currency})

    def orders(self, currency, order_id=None, order_type=None, after=None, count=100):
        return self.query('private', 'orders',
                          {'order_id': order_id, 'type': order_type, 'count': count,
                           'after': after, 'currency': currency})

    def user_transactions(self, currency, searchGb=0, offset=0, count=20):
        return self.query('private', 'user_transactions',
                          {'currency': currency, 'searchGb': searchGb, 'offset': offset, 'count': count})

    def place(self, order_currency, units, price, type, payment_currency="KRW"):
        return self.query('private', 'place', {'order_currency': order_currency, 'Payment_currency': payment_currency,
                                               'units': units, 'price': price, 'type': type})

    def order_detail(self, order_id, type, currency):
        return self.query('private', 'order_detail', {'order_id': order_id, 'type': type, 'currency': currency})

    def cancel(self, type, order_id, currency):
        return self.query('private', 'cancel', {'type': type, 'order_id': order_id, 'currency': currency})

    def btc_withdrawal(self, currency, address, units, destination=None):
        return self.query('private', 'btc_withdrawal', {'units': units, 'address': address,
                                                        'destination': destination, 'currency': currency})

    @deprecation.deprecated()
    def krw_deposit(self):
        return self.query('private', 'krw_deposit', {})

    @deprecation.deprecated()
    def krw_withdrawal(self, bank, account, price):
        return self.query('private', 'krw_withdrawal', {'bank': bank, 'account': account, 'price': price})

    def market_buy(self, units, currency):
        return self.query('private', 'market_buy', {'units': units, 'currency': currency})

    def market_sell(self, units, currency):
        return self.query('private', 'market_sell', {'units': units, 'currency': currency})
