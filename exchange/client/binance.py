import hmac, hashlib
import json
import time
import requests


class BinanceApiClient:

    def __init__(self):
        self.public = []
        self.order = []
        self.host = 'https://www.binance.com'
        self.api_key = 'jfgskZRVPY9Kjgn0T1BNo6DOPXJP6ClemEHqn1lguetX6HI4dXceqONVfCHEYA9B'
        self.api_secret = 'tZbvvgLZbsjVn0yxbTD6q4YejMouHInYnaKo2r6kdAWGJFBXjon1em7tGXZoeEar'

    def send_request(self, method, endpoint, query, private=False):
        if private is True:
            timestamp = lambda: int(round(time.time() * 1000))
            query += "&timestamp=" + str(timestamp())

            signature = hmac.new(bytes(self.api_secret.encode('utf-8')), query.encode('utf-8'), hashlib.sha256).hexdigest()
            query += '&signature=' + signature

            url = self.host + endpoint + "?" + query
            headers = {'X-MBX-APIKEY': self.api_key}
            print(url)
            if method == 'GET':
                r = requests.get(url, headers=headers)
            elif method == 'POST':
                r = requests.post(url, headers=headers)
            elif method == 'DELETE':
                r = requests.delete(url, headers=headers)
        else:
            url = self.host + endpoint + "?" + query
            print(url)
            if method == 'GET':
                r = requests.get(url)
            elif method == 'POST':
                r = requests.post(url)
        return json.loads(r.text)

    """
        Public API
    """
    def orderbook(self, currencypair, limit=None):
        endpoint = '/api/v1/depth'
        query = 'symbol=' + currencypair.upper()
        return self.send_request('GET', endpoint, query)

    def recent_trades_list(self, currencypair, limit=None):
        endpoint = '/api/v1/depth'
        query = 'symbol=' + currencypair.upper()
        return self.send_request('GET', endpoint, query)

    def symbol_price_ticker(self, currencypair=None):
        endpoint = '/api/v3/ticker/price'
        if currencypair is not None:
            query = 'symbol=' + currencypair.upper()
        else:
            query = ''
        return self.send_request('GET', endpoint, query)


    """
        Private API
    """
    def new_order(self, currencypair, side, quantity, price, newClientOrderId=None, stopPrice=None, icebergQty=None, newOrderRespType=None, recvWindow=None):
        endpoint = '/api/v3/order'
        query = 'symbol=' + currencypair.upper() + '&side=' + side + '&type=LIMIT&timeInForce=GTC&quantity=' \
                + str(quantity) + '&price=' + str(price)
        return self.send_request('POST', endpoint, query, private=True)

    def query_order(self, currencypair, orderId=None, origClientOrderId=None, recvWindow=None):
        endpoint = '/api/v3/order'
        query = ''
        if orderId:
            query = 'symbol=' + currencypair.upper() + '&orderId=' + str(orderId)
        elif origClientOrderId:
            query = 'symbol=' + currencypair.upper() + '&origClientOrderId=' + str(origClientOrderId)
        else:
            return False
        return self.send_request('GET', endpoint, query, private=True)

    def cancel_order(self, currencypair, orderId=None, origClientOrderId=None, recvWindow=None):
        endpoint = '/api/v3/order'
        query = ''
        if orderId:
            query = 'symbol=' + currencypair.upper() + '&orderId=' + str(orderId)
        elif origClientOrderId:
            query = 'symbol=' + currencypair.upper() + '&origClientOrderId=' + str(origClientOrderId)
        return self.send_request('DELETE', endpoint, query, private=True)

    def open_orders(self, currencypair=None, recvWindow=None):
        endpoint = '/api/v3/openOrders'
        if currencypair:
            query = 'symbol=' + currencypair.upper()
        else:
            query = ''
        return self.send_request('GET', endpoint, query, private=True)

    def all_orders(self, currencypair, orderId=None, limit=None, recvWindow=None):
        endpoint = '/api/v3/allOrders'
        query = 'symbol=' + currencypair.upper()
        return self.send_request('GET', endpoint, query, private=True)

    def account_information(self, recvWindow=None):
        endpoint = '/api/v3/account'
        query = ''
        return self.send_request('GET', endpoint, query, private=True)

    def account_trade_list(self, currencypair, limit=None, fromId=None, recvWindow=None):
        endpoint = '/api/v3/myTrades'
        query = 'symbol=' + currencypair.upper()
        return self.send_request('GET', endpoint, query, private=True)

    def withdraw(self, asset, address, amount, addressTag=None, name=None, recvWindow=None):
        endpoint = '/wapi/v3/withdraw.html'
        if addressTag:
            query = 'asset=' + asset + '&address=' + address + '&amount=' + str(amount) + '&addressTag=' + addressTag
        else:
            query = 'asset=' + asset + '&address=' + address + '&amount=' + str(amount)
        return self.send_request('POST', endpoint, query, private=True)

    def deposit_history(self, asset=None, status=None, startTime=None, endTime=None, recvWindow=None):
        endpoint = '/wapi/v3/depositHistory.html'
        query = ''
        return self.send_request('GET', endpoint, query, private=True)

    def withdraw_history(self, asset=None, status=None, startTime=None, endTime=None, recvWindow=None):
        endpoint = '/wapi/v3/withdrawHistory.html'
        query = ''
        return self.send_request('GET', endpoint, query, private=True)

    def deposit_address(self, asset, status=None, recvWindow=None):
        endpoint = '/wapi/v3/depositAddress.html'
        query = 'asset=' + asset
        return self.send_request('GET', endpoint, query, private=True)

    def withdraw_fee(self, asset, recvWindow=None):
        endpoint = '/wapi/v3/withdrawFee.html'
        query = ''
        return self.send_request('GET', endpoint, query, private=True)
