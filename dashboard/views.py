import json
from decimal import Decimal

import requests
from django.http import HttpResponseNotFound, HttpResponseBadRequest, HttpResponseServerError
from django.http import HttpResponse

from django.core.cache import cache

from django.views.decorators.csrf import csrf_exempt
from dynamic_preferences.registries import global_preferences_registry
from rest_framework.authentication import TokenAuthentication
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.permissions import IsAuthenticated

from exchange.manager.bithumb import BithumbManager
from exchange.manager.bittrex import BittrexManager
from exchange.symbol import Currency, CurrencyPair
from exchange.models import Exchange, WalletAddress, Currency

from tube.process import Process
from tube.tube_manager import TubeManager

global_preferences = global_preferences_registry.manager()


bithumb_manager = BithumbManager()
bittrex_manager = BittrexManager()

p = Process()
tm = TubeManager()


def json_default(value):
    return str(value)


@api_view(['GET'])
@authentication_classes((TokenAuthentication,))
@permission_classes((IsAuthenticated,))
@csrf_exempt
def tube_find(request):
    from exchange.symbol import Currency, CurrencyPair
    if request.method == 'GET':
        premiums = []

        bithumb_tickers = bithumb_manager.get_ticker()
        bittrex_tickers = bittrex_manager.get_ticker()

        thumb_btc_price = bithumb_tickers[0]["close"]
        #rate_api_r = requests.get("https://free.currencyconverterapi.com/api/v5/convert?q=USD_KRW&compact=y")
        #usd_krw_rate = Decimal(json.loads(rate_api_r.text)['USD_KRW']['val'])
        #rate_api_r = requests.get("http://api.fixer.io/latest?base=USD")
        rate_api_r = requests.get('http://earthquake.kr/exchange')
        usd_krw_rate = Decimal(json.loads(rate_api_r.text)['USDKRW'][0])

        btc_usdt = list(filter(lambda d: str(d['market']) == str(CurrencyPair(Currency('BTC'), Currency('USDT'))),
                               bittrex_tickers))[0]['close']
        gimp_per = (thumb_btc_price - btc_usdt * usd_krw_rate) / thumb_btc_price * 100

        # BTC
        btc_dict = {"currency": "BTC",
                    "thumbPrice": int(thumb_btc_price),
                    "thumbValue": "1",
                    "trexValue": "1",
                    "valueGap": "0",
                    "valueGapPer": "0",
                    "gimpPer": '{0:.2f}'.format(gimp_per)}

        for bithumb_ticker in bithumb_tickers:
            match = list(filter(lambda d: str(d['market'].getcounter()) == str(bithumb_ticker['market'].getcounter())
                                          and d['market'].getbase() == Currency('BTC'), bittrex_tickers))
            if match:
                currency = str(bithumb_ticker['market'].getcounter())
                black_list = global_preferences['dashboard_coinBlackList'].split(',')
                if str(bithumb_ticker['market'].getcounter()) in black_list:
                    continue

                bittrex_ticker = match[0]
                thumb_price = bithumb_ticker['close']
                thumb_value = Decimal(thumb_price / thumb_btc_price)
                trex_value = bittrex_ticker['close']
                value_gap = thumb_value - trex_value
                value_gap_per = value_gap / trex_value * 100
                gimp_per = (thumb_price - trex_value * btc_usdt * usd_krw_rate) / thumb_price * 100
                premiums.append({"currency": currency,
                                 "thumbPrice": int(thumb_price),
                                 "thumbValue": '{0:.8f}'.format(thumb_value),
                                 "trexValue": '{0:.8f}'.format(trex_value),
                                 "valueGap": '{0:.8f}'.format(value_gap),
                                 "valueGapPer": '{0:.2f}'.format(value_gap_per),
                                 "gimpPer": '{0:.2f}'.format(gimp_per)})

        sorted_premiums = sorted(premiums, key=lambda k: float(k['valueGapPer']))
        src = sorted_premiums[:3]
        dest = sorted_premiums[:-4:-1]

        response_data = {'src': src,
                         'dest': dest,
                         'premiums': [btc_dict] + premiums}

        return HttpResponse(json.dumps(response_data), content_type="application/json")
    else:
        response_data = {'error': 'allowed only by GET'}
        return HttpResponseBadRequest(json.dumps(response_data, default=json_default), content_type="application/json")


@api_view(['GET', 'POST', 'PUT', 'DELETE'])
@authentication_classes((TokenAuthentication,))
@permission_classes((IsAuthenticated,))
@csrf_exempt
def tube(request, tube_id=None):
    #auth = request.META['HTTP_AUTHORIZATION']

    if request.method == 'GET' and tube_id is not None:
        return tube_desc(tube_id)
    elif request.method == 'GET':
        return tube_list()
    elif request.method == 'POST':
        return tube_init(request)
    elif request.method == 'PUT' and tube_id is not None:
        return tube_coin(request, tube_id)
    elif request.method == 'DELETE' and tube_id is not None:
        print("delete!!!")
        return tube_cancel(request, tube_id)
    else:
        response_data = {'error': 'Bad Request'}
        return HttpResponseBadRequest(json.dumps(response_data, default=json_default), content_type="application/json")


def tube_init(request):
    try:
        body = json.loads(request.body)
        init_price = int(body['initPrice'])

        tube_info = cache.get('tube_info')
        if tube_info:
            raise RuntimeError('Tube is running')

        p.set_init_krw(init_price)

        response_data = {'initPrice': init_price}

        return HttpResponse(json.dumps(response_data), content_type="application/json")
    except Exception as ex:
        response_data = {'error': ex}
        return HttpResponseServerError(json.dumps(response_data, default=json_default), content_type="application/json")


def tube_list():
    tubes = []

    tube_info = cache.get('tube_info')

    if tube_info is not None:
        tube_id = tube_info['tube_id']
        step_now = tube_info['step_now']
        tubes.append({"tubeId": tube_id,
                      "stepNow": step_now})

    response_data = {'tubes': tubes}

    return HttpResponse(json.dumps(response_data), content_type="application/json")


def tube_desc(tube_id):
    tube_info = cache.get('tube_info')
    tube_steps = cache.get_many(cache.keys('%s:*' % tube_id))

    if tube_steps:
        init_price = tube_steps['%s:1' % tube_id]['init_price']

        steps = []
        for i in range(1, len(tube_steps) + 1):
            steps.append(tube_steps['%s:%d' % (tube_id, i)])

        response_data = {'tubeId': tube_id,
                         'stepNow': tube_info['step_now'],
                         'initPrice': init_price,
                         'steps': steps}

        return HttpResponse(json.dumps(response_data, default=json_default), content_type="application/json")
    else:
        response_data = {'error': 'Not exist tube'}
        return HttpResponseNotFound(json.dumps(response_data, default=json_default), content_type="application/json")


def tube_coin(request, tube_id):
    try:
        body = json.loads(request.body)

        tube_info = cache.get('tube_info')
        if tube_info is None:
            raise RuntimeError('Tube is not running')

        coin_symbol = body['coin']
        step_now = tube_info['step_now']
        thumb_alt_price = int(body['thumb_alt_price'])
        trex_alt_value = Decimal(body['trex_alt_value'])
        if step_now == 1:
            p.select_bithumb_altcoin(tube_info['tube_id'], coin_symbol, thumb_alt_price, trex_alt_value)
            tm.stage1()
            response_data = {'exchange': 'bithumb',
                             'coin': coin_symbol,
                             'thumb_alt_price': thumb_alt_price,
                             'trex_alt_value': trex_alt_value}
            return HttpResponse(json.dumps(response_data, default=json_default), content_type="application/json")
        elif step_now == 9:
            p.select_bittrex_altcoin(tube_info['tube_id'], coin_symbol, trex_alt_value, thumb_alt_price)
            response_data = {'exchange': 'bittrex',
                             'coin': coin_symbol,
                             'trex_alt_value': trex_alt_value,
                             'thumb_alt_price': thumb_alt_price}
            return HttpResponse(json.dumps(response_data, default=json_default), content_type="application/json")
        else:
            response_data = {'error': "Not available method in step"}
            return HttpResponseBadRequest(json.dumps(response_data, default=json_default),
                                           content_type="application/json")

    except Exception as ex:
        response_data = {'error': ex}
        return HttpResponseServerError(json.dumps(response_data, default=json_default), content_type="application/json")


def tube_cancel(request, tube_id):
    try:
        tube_info = cache.get('tube_info')
        running_tube_id = tube_info['tube_id']
        if tube_id != running_tube_id:
            raise RuntimeError('Tube is not running')

        tube_steps = cache.get_many(cache.keys('%s:*' % tube_id))

        if tube_steps:
            last_step = tube_steps['%s:%d' % (tube_id, len(tube_steps))]
            tube_step = last_step['tube_step']
            p.cancel(tube_id, tube_step)

            response_data = {'tubeId': tube_id}

            return HttpResponse(json.dumps(response_data, default=json_default), content_type="application/json")
        else:
            raise RuntimeError('Unknown error occured.')

    except Exception as ex:
        response_data = {'error': ex}
        return HttpResponseServerError(json.dumps(response_data, default=json_default), content_type="application/json")


@csrf_exempt
def wallet_address_list(request, exchange):
    exchange = Exchange.objects.get(name=exchange)
    if request.method == 'GET':
        wal_add_list = []
        query_list = WalletAddress.objects.filter(exchange_id=exchange)
        for query in query_list:
            cid = query.currency_id
            coin_symbol = Currency.objects.get(id=cid).symbol
            add = query.address
            tag = query.tag
            wal_add_list.append({"coin": coin_symbol, "address": add, "tag": tag})
        return HttpResponse(json.dumps(wal_add_list, default=json_default), content_type="application/json")

    elif request.method == 'POST':
        body = json.loads(request.body)
        coin_symbol = body['coin_symbol'].upper()
        address = body['address']
        tag = body['tag']

        coin = Currency.objects.get(symbol=coin_symbol)
        wal_add = WalletAddress.objects.create(address=address, tag=tag, currency_id=coin.id, exchange_id=exchange.id)
        wal_add.save()

        return HttpResponse(status=201)


@csrf_exempt
def wallet_address(request, exchange, coin_symbol):
    if request.method == 'DELETE':
        exchange = Exchange.objects.get(name=exchange)
        coin = Currency.objects.get(symbol=coin_symbol)
        WalletAddress.objects.get(exchange_id=exchange.id, currency_id=coin.id).delete()
        return HttpResponse(status=200)
