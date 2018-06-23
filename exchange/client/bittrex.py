from urllib.parse import urlencode
import urllib.request
import json
import time
import hmac
import hashlib
import ssl

from dynamic_preferences.registries import global_preferences_registry

global_preferences = global_preferences_registry.manager()


class BittrexApiClient:

    def __init__(self):
        self.public = ['getmarkets', 'getcurrencies', 'getticker', 'getmarketsummaries', 'getmarketsummary',
                       'getorderbook', 'getmarkethistory']
        self.market = ['buylimit', 'buymarket', 'selllimit', 'sellmarket', 'cancel', 'getopenorders']
        self.account = ['getbalances', 'getbalance', 'getdepositaddress', 'withdraw', 'getorder', 'getorderhistory',
                        'getwithdrawalhistory', 'getdeposithistory']

    def query(self, method, values={}):
        if method in self.public:
            url = 'https://bittrex.com/api/v1.1/public/'
        elif method in self.market:
            url = 'https://bittrex.com/api/v1.1/market/'
        elif method in self.account:
            url = 'https://bittrex.com/api/v1.1/account/'
        else:
            #TODO raise exception
            return 'Something went wrong, sorry.'

        url += method + '?' + urlencode(values)

        if method not in self.public:
            url += '&apikey=' + global_preferences['exchange_bittrexApiKey']
            url += '&nonce=' + str(int(time.time()))
            signature = hmac.new(bytes(global_preferences['exchange_bittrexApiSecret'].encode('utf-8')), url.encode('utf-8'), hashlib.sha512).hexdigest()
            headers = {'apisign': signature}
        else:
            headers = {}

        req = urllib.request.Request(url, headers=headers)
        gcontext = ssl.SSLContext(ssl.PROTOCOL_SSLv23)
        response = json.loads(urllib.request.urlopen(req, context=gcontext).read())
        return response

    def getmarkets(self):
        return self.query('getmarkets')

    def getcurrencies(self):
        return self.query('getcurrencies')

    def getticker(self, market):
        return self.query('getticker', {'market': market})

    def getmarketsummaries(self):
        return self.query('getmarketsummaries')

    def getmarketsummary(self, market):
        return self.query('getmarketsummary', {'market': market})

    def getorderbook(self, market, type, depth=20):
        return self.query('getorderbook', {'market': market, 'type': type, 'depth': depth})

    def getmarkethistory(self, market, count=20):
        return self.query('getmarkethistory', {'market': market, 'count': count})

    def buylimit(self, market, quantity, rate):
        return self.query('buylimit', {'market': market, 'quantity': quantity, 'rate': rate})

    def buymarket(self, market, quantity):
        return self.query('buymarket', {'market': market, 'quantity': quantity})

    def selllimit(self, market, quantity, rate):
        return self.query('selllimit', {'market': market, 'quantity': quantity, 'rate': rate})

    def sellmarket(self, market, quantity):
        return self.query('sellmarket', {'market': market, 'quantity': quantity})

    def cancel(self, uuid):
        return self.query('cancel', {'uuid': uuid})

    def getopenorders(self, market):
        return self.query('getopenorders', {'market': market})

    def getbalances(self):
        return self.query('getbalances')

    def getbalance(self, currency):
        return self.query('getbalance', {'currency': currency})

    def getdepositaddress(self, currency):
        return self.query('getdepositaddress', {'currency': currency})

    def withdraw(self, currency, address, quantity, paymentid=None):
        if paymentid is None:
            return self.query('withdraw', {'currency': currency, 'quantity': quantity, 'address': address})
        else:
            return self.query('withdraw',
                              {'currency': currency, 'quantity': quantity, 'address': address, 'paymentid': paymentid})

    def getorder(self, uuid):
        return self.query('getorder', {'uuid': uuid})

    def getorderhistory(self, market, count):
        return self.query('getorderhistory', {'market': market, 'count': count})

    def getwithdrawalhistory(self, currency, count):
        return self.query('getwithdrawalhistory', {'currency': currency, 'count': count})

    def getdeposithistory(self, currency, count):
        return self.query('getdeposithistory', {'currency': currency, 'count': count})
