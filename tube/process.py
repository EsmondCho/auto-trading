from datetime import datetime
from decimal import Decimal, ROUND_DOWN
from django.core.cache import cache
from dynamic_preferences.registries import global_preferences_registry

import exchange
from exchange.manager.bithumb import BithumbManager
from exchange.manager.bittrex import BittrexManager
from exchange.models import WalletAddress, WithdrawalFee
from exchange.symbol import CurrencyPair
from tube import telegram_handler, tube_manager


global_preferences = global_preferences_registry.manager()

bithumb_manager = BithumbManager()
bittrex_manager = BittrexManager()


def is_exist_oid(r, order_id):
    for d in r:
        if d['id'] == order_id:
            return True
    return False


def set_step_now(tube_id, step_now):
    tube_info_value = {"tube_id": tube_id,
                       "step_now": step_now}
    cache.set("tube_info", tube_info_value, timeout=None)


def get_cache_value(tube_id, step, key):
    get_key = "%s:%s" % (tube_id, step)
    get_value = cache.get(get_key)
    return get_value[key]


class Process:

    #1 초기입력 & 허매수_bithumb
    def set_init_krw(self, init_price):
        #허매수
        currencypair = CurrencyPair(exchange.symbol.Currency('BTC'), exchange.symbol.Currency('KRW'))
        ticker = bithumb_manager.get_ticker(currencypair)
        price = int(round(ticker[0]['close'] * Decimal('0.2'), -3))
        amount = Decimal(init_price / price).quantize(Decimal('.0001'), rounding=ROUND_DOWN)
        tube_id = bithumb_manager.bid(currencypair, amount, price)

        tube_step = 1
        executed_time = datetime.now()

        #redis
        key = "%s:%s" % (tube_id, tube_step)
        value = {"tube_id": tube_id,
                 "tube_step": tube_step,
                 "executed_time": executed_time,
                 "init_price": init_price,
                 "price": init_price,
                 "desc": "Created Tube",
                 "celery_checked": False}
        cache.set(key, value, timeout=None)

        msg = "튜브가 생성되었습니다.\nTube ID : %s번, 총액 : %s원" % (tube_id, init_price)
        telegram_handler.alert_admin(msg)

        set_step_now(tube_id, tube_step)


    #2 altcoin 선택_bithumb
    def select_bithumb_altcoin(self, tube_id, coin_symbol, thumb_alt_price, trex_alt_value):
        step_val = cache.get(tube_id+":"+str(2))
        if step_val is not None:
            if step_val['celery_checked'] is True:
                return False

        #get step 1 data
        init_price = get_cache_value(tube_id, 1, "init_price")
        bid_alt_code = exchange.symbol.Currency(coin_symbol.upper())
        bid_alt_amt = Decimal(init_price / thumb_alt_price).quantize(Decimal('.0001'), rounding=ROUND_DOWN) #TODO 거래소 api 단계? 처리 필요

        # redis
        tube_step = 2
        executed_time = datetime.now()
        set_key = "%s:%s" % (tube_id, tube_step)
        set_value = {"tube_id": tube_id,
                     "tube_step": tube_step,
                     "executed_time": executed_time,
                     "bid_alt_code": bid_alt_code,
                     "bid_alt_amt": bid_alt_amt,
                     "thumb_alt_price": thumb_alt_price,
                     "trex_alt_value": trex_alt_value,
                     "price": init_price,
                     "desc": "Select Coin in Bithumb",
                     "celery_checked": False}
        cache.set(set_key, set_value, timeout=None)

        set_step_now(tube_id, tube_step)

    #3 허매수 취소 & bid 신청_bithumb
    def bithumb_bid(self, tube_id):
        step_val = cache.get(tube_id+":"+str(3))
        if step_val is not None:
            if step_val['celery_checked'] is True:
                return False

        #get step 2
        bid_alt_code = get_cache_value(tube_id, 2, "bid_alt_code")
        bid_alt_amt = get_cache_value(tube_id, 2, "bid_alt_amt")
        thumb_alt_price = get_cache_value(tube_id, 2, "thumb_alt_price")
        trex_alt_value = get_cache_value(tube_id, 2, "trex_alt_value")

        #허매수 취소
        cp = CurrencyPair(exchange.symbol.Currency('BTC'), exchange.symbol.Currency('KRW'))
        bithumb_manager.cancel(tube_id, cp, 'bid')

        #주문
        currencypair = CurrencyPair(bid_alt_code, exchange.symbol.Currency('KRW'))
        bid_order_id = bithumb_manager.bid(currencypair, bid_alt_amt, thumb_alt_price)

        thumb_btc_ticker = bithumb_manager.get_ticker(CurrencyPair(exchange.symbol.Currency('BTC'),
                                                                   exchange.symbol.Currency('KRW')))
        thumb_btc_price = int(thumb_btc_ticker[0]['close'])
        thumb_alt_value = Decimal(thumb_alt_price / thumb_btc_price).quantize(Decimal('.00000001'), rounding=ROUND_DOWN)

        # redis
        tube_step = 3
        executed_time = datetime.now()
        set_key = "%s:%s" % (tube_id, tube_step)
        set_value = {"tube_id": tube_id,
                     "tube_step": tube_step,
                     "executed_time": executed_time,
                     "bid_order_id": bid_order_id,
                     "bid_alt_code": bid_alt_code,
                     "bid_alt_amt": bid_alt_amt,
                     "thumb_alt_price": thumb_alt_price,
                     "thumb_btc_price": thumb_btc_price,
                     "thumb_alt_value": thumb_alt_value,
                     "trex_alt_value": trex_alt_value,
                     "price": int(Decimal(thumb_alt_price) * bid_alt_amt),
                     "desc": "Start Biding in Bithumb...",
                     "celery_checked": False}
        cache.set(set_key, set_value, timeout=None)

        # set_step_now(tube_id, tube_step) # celery check_orderbook() 메소드가 할 것임
        #TODO stepnow와 step갯수 불일치

    #4 bid 완료_bithumb
    def bithumb_bid_complete(self, tube_id):
        step_val = cache.get(tube_id+":"+str(4))
        if step_val is not None:
            if step_val['celery_checked'] is True:
                return False

        # get step 3
        bid_alt_code = get_cache_value(tube_id, 3, "bid_alt_code")
        bid_alt_amt = get_cache_value(tube_id, 3, "bid_alt_amt")

        step_2_et = get_cache_value(tube_id, 2, "executed_time")

        # calc bid amount
        currencypair = CurrencyPair(bid_alt_code, exchange.symbol.Currency('KRW'))
        r = bithumb_manager.get_order_history(currencypair)
        match = list(filter(lambda history: history['date'] > step_2_et and history['type'] == 'bid', r))
        amount = Decimal(0)
        total = Decimal(0)
        for h in match:
            amount = amount + h["amount"]
            total = total + h["price"] * h["amount"]
        thumb_alt_price = (total / amount).quantize(Decimal('0.00000001'), rounding=ROUND_DOWN)

        msg = "빗썸에서 %s 매수 체결.\n가격 : %d원, 수량 : %.4f, 총액 : %d원" %\
              (bid_alt_code, thumb_alt_price, bid_alt_amt,
               int(thumb_alt_price * bid_alt_amt))
        telegram_handler.alert_admin(msg)

        # redis
        tube_step = 4
        executed_time = datetime.now()
        set_key = "%s:%s" % (tube_id, tube_step)
        set_value = {"tube_id": tube_id,
                     "tube_step": tube_step,
                     "executed_time": executed_time,
                     "price": int(bid_alt_amt * thumb_alt_price),
                     "desc": "Bid Complete in Bithumb",
                     "celery_checked": False}
        cache.set(set_key, set_value, timeout=None)

        set_step_now(tube_id, tube_step)

    #5 withdrawal 신청_bithumb
    def bithumb_withdrawal(self, tube_id):
        step_val = cache.get(tube_id+":"+str(5))
        if step_val is not None:
            if step_val['celery_checked'] is True:
                return False

        #get step 3
        step_3_bid_alt_amt = get_cache_value(tube_id, 3, "bid_alt_amt")
        fee = step_3_bid_alt_amt * Decimal(str(global_preferences['tube_bithumbTransactionFee'])) * Decimal('0.01')
        bid_alt_amt = (step_3_bid_alt_amt - fee).quantize(Decimal('.0001'), rounding=ROUND_DOWN) #TODO 수수료 계산 구현 당시에는 order history api를 사용하지 않았음. 현재는 정산 금액을 기준으로 수량을 감지하도록 수정 필요
        thumb_out_alt_code = get_cache_value(tube_id, 3, "bid_alt_code")

        wallet_address = WalletAddress.objects.filter(exchange__id=2, currency__symbol=thumb_out_alt_code).get()
        address = wallet_address.address
        tag = wallet_address.tag
        withdrawal_fee = WithdrawalFee.objects.filter(exchange__id=1, currency__symbol=thumb_out_alt_code).get().fee
        thumb_out_alt_amt = bid_alt_amt - withdrawal_fee

        if tag is not None: #TODO tag API단에서 처리
            bithumb_manager.withdrawal(thumb_out_alt_code, address, thumb_out_alt_amt, tag)
        else:
            bithumb_manager.withdrawal(thumb_out_alt_code, address, thumb_out_alt_amt)

        price = int(Decimal(cache.get("%s:%s" % (tube_id, 4))["price"])
                    * (Decimal('1.0') - Decimal(str(global_preferences['tube_bithumbTransactionFee'])) * Decimal('0.01')))

        # redis
        tube_step = 5
        executed_time = datetime.now()
        set_key = "%s:%s" % (tube_id, tube_step)
        set_value = {"tube_id": tube_id,
                     "tube_step": tube_step,
                     "executed_time": executed_time,
                     "thumb_out_alt_code": thumb_out_alt_code,
                     "thumb_out_alt_amt": thumb_out_alt_amt,
                     "price": price,
                     "desc": "Start Withdrawal in Bithumb",
                     "celery_checked": False}
        cache.set(set_key, set_value, timeout=None)

    #6 withdrawal 완료_bithumb
    def bithumb_withdrawal_complete(self, tube_id):
        step_val = cache.get(tube_id+":"+str(6))
        if step_val is not None:
            if step_val['celery_checked'] is True:
                return False

        # get step 5
        thumb_out_alt_amt = get_cache_value(tube_id, 5, "thumb_out_alt_amt")
        thumb_out_alt_code = get_cache_value(tube_id, 5, "thumb_out_alt_code")
        price = get_cache_value(tube_id, 5, "price")

        msg = "빗썸에서 %f%s 출금 완료." % (thumb_out_alt_amt, thumb_out_alt_code)
        telegram_handler.alert_admin(msg)

        # redis
        tube_step = 6
        executed_time = datetime.now()
        set_key = "%s:%s" % (tube_id, tube_step)
        set_value = {"tube_id": tube_id,
                     "tube_step": tube_step,
                     "executed_time": executed_time,
                     "price": price,
                     "desc": "Withdrawal Complete in Bithumb",
                     "celery_checked": False}
        cache.set(set_key, set_value, timeout=None)

    #7 deposit 완료_bittrex
    def bittrex_deposit_complete(self, tube_id):
        step_val = cache.get(tube_id+":"+str(7))
        if step_val is not None:
            if step_val['celery_checked'] is True:
                return False

        # get step 5
        trex_in_alt_code = get_cache_value(tube_id, 5, "thumb_out_alt_code")
        trex_in_alt_amt = get_cache_value(tube_id, 5, "thumb_out_alt_amt")
        price = get_cache_value(tube_id, 5, "price")

        # get step 5
        msg = "Bittrex에 %f%s 입금 완료." % (trex_in_alt_amt, trex_in_alt_code)
        telegram_handler.alert_admin(msg)

        tube_step = 7
        executed_time = datetime.now()

        # redis
        set_key = "%s:%s" % (tube_id, tube_step)
        set_value = {"tube_id": tube_id,
                     "tube_step": tube_step,
                     "executed_time": executed_time,
                     "trex_in_alt_code": trex_in_alt_code,
                     "trex_in_alt_amt": trex_in_alt_amt,
                     "price": price,
                     "desc": "Deposit Complete in Bittrex",
                     "celery_checked": False}
        cache.set(set_key, set_value, timeout=None)

        set_step_now(tube_id, tube_step)

    #8 ask 신청_bittrex
    def bittrex_ask_to_btc(self, tube_id):
        step_val = cache.get(tube_id + ":" + str(8))
        if step_val is not None:
            if step_val['celery_checked'] is True:
                return False

        # get step 7
        ask_alt_code = get_cache_value(tube_id, 7, "trex_in_alt_code")
        ask_alt_amt = get_cache_value(tube_id, 7, "trex_in_alt_amt")

        currencypair = CurrencyPair(ask_alt_code, exchange.symbol.Currency('BTC'))
        trex_alt_value = cache.get("%s:%s" % (tube_id, 3))["trex_alt_value"]

        # 주문
        ask_order_id = bittrex_manager.ask(currencypair, ask_alt_amt, trex_alt_value)

        thumb_btc_ticker = bithumb_manager.get_ticker(CurrencyPair(exchange.symbol.Currency('BTC'),
                                                                   exchange.symbol.Currency('KRW')))
        thumb_btc_price = int(thumb_btc_ticker[0]['close'])
        thumb_alt_ticker = bithumb_manager.get_ticker(CurrencyPair(ask_alt_code, exchange.symbol.Currency('KRW')))
        thumb_alt_price = int(thumb_alt_ticker[0]['close'])
        thumb_alt_value = Decimal(thumb_alt_price / thumb_btc_price).quantize(Decimal('0.00000001'), rounding=ROUND_DOWN)

        tube_step = 8
        executed_time = datetime.now()

        # redis
        set_key = "%s:%s" % (tube_id, tube_step)
        set_value = {"tube_id": tube_id,
                     "tube_step": tube_step,
                     "executed_time": executed_time,
                     "ask_alt_code": ask_alt_code,
                     "ask_alt_amt": ask_alt_amt,
                     "ask_order_id": ask_order_id,
                     "thumb_btc_price": thumb_btc_price,
                     "thumb_alt_price": thumb_alt_price,
                     "thumb_alt_value": thumb_alt_value,
                     "trex_alt_value": trex_alt_value,
                     "price": int(Decimal(thumb_alt_price) * ask_alt_amt),
                     "desc": "Start Asking in Bittrex...",
                     "celery_checked": False}
        cache.set(set_key, set_value, timeout=None)

        # set_step_now(tube_id, tube_step) # celery check_orderbook() 메소드가 할 것임

    #9 ask 완료_bittrex
    def bittrex_ask_to_btc_complete(self, tube_id):
        step_val = cache.get(tube_id + ":" + str(9))
        if step_val is not None:
            if step_val['celery_checked'] is True:
                return False

        # get step 8
        ask_alt_code = get_cache_value(tube_id, 8, "ask_alt_code")
        ask_alt_amt = get_cache_value(tube_id, 8, "ask_alt_amt")
        step_7_et = get_cache_value(tube_id, 7, "executed_time")
        thumb_alt_price = get_cache_value(tube_id, 8, "thumb_alt_price")

        currencypair = CurrencyPair(ask_alt_code, exchange.symbol.Currency('BTC'))
        r = bittrex_manager.get_order_history(currencypair)
        match = list(filter(lambda history: history['date'] > step_7_et and history['type'] == 'ask', r))
        amount = Decimal(0)
        total = Decimal(0)
        for h in match:
            amount = amount + h["amount"]
            total = total + h["price"] * h["amount"]
        trex_alt_value = (total / amount).quantize(Decimal('0.00000001'), rounding=ROUND_DOWN)

        msg = "Bittrex에서 %s 매도 체결.\n가격 : %.8fBTC, 수량 : %.8f%s, 총액 : %.8fBTC" %\
              (ask_alt_code, trex_alt_value, ask_alt_amt,
               ask_alt_code, trex_alt_value * ask_alt_amt)
        telegram_handler.alert_admin(msg)

        tube_step = 9
        executed_time = datetime.now()

        # redis
        set_key = "%s:%s" % (tube_id, tube_step)
        set_value = {"tube_id": tube_id,
                     "tube_step": tube_step,
                     "executed_time": executed_time,
                     "price": int(Decimal(thumb_alt_price) * ask_alt_amt),
                     "desc": "Ask Complete in Bittrex",
                     "celery_checked": False}
        cache.set(set_key, set_value, timeout=None)

        set_step_now(tube_id, tube_step)

    #10 altcoin 선택_bittrex
    def select_bittrex_altcoin(self, tube_id, coin_symbol, trex_alt_value, thumb_alt_price):
        ti = cache.get("tube_info")
        if ti["step_now"] != 9:
            print("아직 사용할 수 없습니다.")
            return

        step_val = cache.get(tube_id + ":" + str(10))
        if step_val is not None:
            if step_val['celery_checked'] is True:
                return False

        # get step 8 data
        ask_alt_amt = get_cache_value(tube_id, 8, "ask_alt_amt")
        ask_alt_value = get_cache_value(tube_id, 8, "trex_alt_value")
        bid_alt_amt = (ask_alt_value
                       * ask_alt_amt
                       * (Decimal('1.0') - Decimal(str(global_preferences['tube_bittrexTransactionFee'])) * Decimal('0.01'))).quantize(Decimal('.00000001'), rounding=ROUND_DOWN)
        bid_alt_code = exchange.symbol.Currency(coin_symbol.upper())

        tube_step = 10
        executed_time = datetime.now()

        price = int(Decimal(cache.get("%s:%s" % (tube_id, 9))["price"])
                    * (Decimal('1.0') - Decimal(str(global_preferences['tube_bittrexTransactionFee'])) * Decimal('0.01')))

        # redis
        set_key = "%s:%s" % (tube_id, tube_step)
        set_value = {"tube_id": tube_id,
                     "tube_step": tube_step,
                     "executed_time": executed_time,
                     "bid_alt_code": bid_alt_code,
                     "bid_alt_amt": bid_alt_amt,
                     "trex_alt_value": trex_alt_value,
                     "thumb_alt_price": thumb_alt_price,
                     "price": price,
                     "desc": "Select coin in Bittrex",
                     "celery_checked": False}
        cache.set(set_key, set_value, timeout=None)

        set_step_now(tube_id, tube_step)

    #11 bid 신청_bittrex
    def bittrex_bid(self, tube_id):
        step_val = cache.get(tube_id + ":" + str(11))
        if step_val is not None:
            if step_val['celery_checked'] is True:
                return False

        # get step 10 data
        bid_alt_code = get_cache_value(tube_id, 10, "bid_alt_code")
        trex_alt_value = get_cache_value(tube_id, 10, "trex_alt_value")
        thumb_alt_price = get_cache_value(tube_id, 10, "thumb_alt_price")
        btc_amt = get_cache_value(tube_id, 10, "bid_alt_amt")
        bid_alt_amt = (btc_amt / trex_alt_value
                       * (Decimal('1.0') - Decimal(str(global_preferences['tube_bittrexTransactionFee'])) * Decimal('0.01'))).quantize(Decimal('.00000001'), rounding=ROUND_DOWN)
        price = get_cache_value(tube_id, 10, "price")

        # 주문
        currencypair = CurrencyPair(bid_alt_code, exchange.symbol.Currency('BTC'))
        bid_order_id = bittrex_manager.bid(currencypair, bid_alt_amt, trex_alt_value)

        thumb_btc_ticker = bithumb_manager.get_ticker(CurrencyPair(exchange.symbol.Currency('BTC'),
                                                                   exchange.symbol.Currency('KRW')))
        thumb_btc_price = int(thumb_btc_ticker[0]['close'])
        thumb_alt_value = Decimal(thumb_alt_price / thumb_btc_price).quantize(Decimal('.00000001'), rounding=ROUND_DOWN)

        tube_step = 11
        executed_time = datetime.now()

        # redis
        set_key = "%s:%s" % (tube_id, tube_step)
        set_value = {"tube_id": tube_id,
                     "tube_step": tube_step,
                     "executed_time": executed_time,
                     "bid_order_id": bid_order_id,
                     "bid_alt_code": bid_alt_code,
                     "bid_alt_amt": bid_alt_amt,
                     "thumb_btc_price": thumb_btc_price,
                     "thumb_alt_price": thumb_alt_price,
                     "thumb_alt_value": thumb_alt_value,
                     "trex_alt_value": trex_alt_value,
                     "price": price,
                     "desc": "Start biding in Bittrex...",
                     "celery_checked": False}
        cache.set(set_key, set_value, timeout=None)

        # set_step_now(tube_id, tube_step) # celery check_orderbook() 메소드가 할 것임

    #12 bid 완료_bittrex
    def bittrex_bid_complete(self, tube_id):
        step_val = cache.get(tube_id + ":" + str(12))
        if step_val is not None:
            if step_val['celery_checked'] is True:
                return False

        # get step 11
        bid_alt_code = get_cache_value(tube_id, 11, "bid_alt_code")
        bid_alt_amt = get_cache_value(tube_id, 11, "bid_alt_amt")

        step_10_et = get_cache_value(tube_id, 10, "executed_time")

        currencypair = CurrencyPair(bid_alt_code, exchange.symbol.Currency('BTC'))
        r = bittrex_manager.get_order_history(currencypair)
        match = list(filter(lambda history: history['date'] > step_10_et and history['type'] == 'bid', r))
        amount = Decimal(0)
        total = Decimal(0)
        for h in match:
            amount = amount + h["amount"]
            total = total + h["price"] * h["amount"]
        trex_alt_value = (total / amount).quantize(Decimal('0.00000001'), rounding=ROUND_DOWN)

        msg = "Bittrex에서 %s 매수 체결.\n가격 : %.8f, 수량 : %.8f, 총액 : %.8fBTC" %\
              (bid_alt_code, trex_alt_value, bid_alt_amt,
               trex_alt_value * bid_alt_amt)
        telegram_handler.alert_admin(msg)

        tube_step = 12
        executed_time = datetime.now()

        thumb_alt_price = get_cache_value(tube_id, 11, "thumb_alt_price")

        # redis
        set_key = "%s:%s" % (tube_id, tube_step)
        set_value = {"tube_id": tube_id,
                     "tube_step": tube_step,
                     "executed_time": executed_time,
                     "price": int(bid_alt_amt * thumb_alt_price),
                     "desc": "Bid Complete in Bittrex",
                     "celery_checked": False}
        cache.set(set_key, set_value, timeout=None)

        set_step_now(tube_id, tube_step)

    #13 withdrawal 신청 bittrex
    def bittrex_withdrawal(self, tube_id):
        step_val = cache.get(tube_id + ":" + str(13))
        if step_val is not None:
            if step_val['celery_checked'] is True:
                return False

        # get step 11
        bid_alt_amt = get_cache_value(tube_id, 11, "bid_alt_amt")
        trex_out_alt_code = get_cache_value(tube_id, 11, "bid_alt_code")

        wallet_address = WalletAddress.objects.filter(exchange__id=1, currency__symbol=trex_out_alt_code).get()
        address = wallet_address.address
        tag = wallet_address.tag
        withdrawal_fee = WithdrawalFee.objects.filter(exchange__id=2, currency__symbol=trex_out_alt_code).get().fee
        trex_out_alt_amt = bid_alt_amt - withdrawal_fee

        if wallet_address.tag is not None:
            bittrex_manager.withdrawal(trex_out_alt_code, address, bid_alt_amt, tag)
        else:
            bittrex_manager.withdrawal(trex_out_alt_code, address, bid_alt_amt)

        thumb_alt_price = get_cache_value(tube_id, 11, "thumb_alt_price")
        price = int(Decimal(thumb_alt_price) * trex_out_alt_amt)

        tube_step = 13
        executed_time = datetime.now()

        # redis
        set_key = "%s:%s" % (tube_id, tube_step)
        set_value = {"tube_id": tube_id,
                     "tube_step": tube_step,
                     "executed_time": executed_time,
                     "trex_out_alt_code": trex_out_alt_code,
                     "trex_out_alt_amt": trex_out_alt_amt,
                     "price": price,
                     "desc": "Start Withdrawal in Bittrex...",
                     "celery_checked": False}
        cache.set(set_key, set_value, timeout=None)

    #14 withdrawal 완료_bittrex
    def bittrex_withdrawal_complete(self, tube_id):
        step_val = cache.get(tube_id + ":" + str(14))
        if step_val is not None:
            if step_val['celery_checked'] is True:
                return False

        # get step 13
        trex_out_alt_amt = get_cache_value(tube_id, 13, "trex_out_alt_amt")
        trex_out_alt_code = get_cache_value(tube_id, 13, "trex_out_alt_code")
        msg = "Bittrex에서 %f%s 출금 완료." % (trex_out_alt_amt, trex_out_alt_code)
        telegram_handler.alert_admin(msg)

        price = get_cache_value(tube_id, 13, "price")

        tube_step = 14
        executed_time = datetime.now()

        # redis
        set_key = "%s:%s" % (tube_id, tube_step)
        set_value = {"tube_id": tube_id,
                     "tube_step": tube_step,
                     "executed_time": executed_time,
                     "price": price,
                     "desc": "Withdrawal complete in Bittrex",
                     "celery_checked": False}
        cache.set(set_key, set_value, timeout=None)

    #15 deposit 완료_bithumb
    def bithumb_deposit_complete(self, tube_id):
        step_val = cache.get(tube_id + ":" + str(15))
        if step_val is not None:
            if step_val['celery_checked'] is True:
                return False

        thumb_in_alt_code = get_cache_value(tube_id, 13, "trex_out_alt_code")
        thumb_in_alt_amt = get_cache_value(tube_id, 13, "trex_out_alt_amt")

        msg = "빗썸에 %f%s 입금 완료." % (thumb_in_alt_amt, thumb_in_alt_code)
        telegram_handler.alert_admin(msg)

        price = get_cache_value(tube_id, 13, "price")

        tube_step = 15
        executed_time = datetime.now()

        # redis
        set_key = "%s:%s" % (tube_id, tube_step)
        set_value = {"tube_id": tube_id,
                     "tube_step": tube_step,
                     "executed_time": executed_time,
                     "thumb_in_alt_code": thumb_in_alt_code,
                     "thumb_in_alt_amt": thumb_in_alt_amt,
                     "price": price,
                     "desc": "Deposit Complete in Bithumb",
                     "celery_checked": False}
        cache.set(set_key, set_value, timeout=None)

        set_step_now(tube_id, tube_step)

    #16 ask 신청_bithumb
    def bithumb_sell(self, tube_id):
        step_val = cache.get(tube_id + ":" + str(16))
        if step_val is not None:
            if step_val['celery_checked'] is True:
                return False

        ask_alt_code = get_cache_value(tube_id, 15, "thumb_in_alt_code")
        ask_alt_amt = get_cache_value(tube_id, 15, "thumb_in_alt_amt").quantize(Decimal('.0001'), rounding=ROUND_DOWN)

        currencypair = CurrencyPair(ask_alt_code, exchange.symbol.Currency('KRW'))
        thumb_alt_price = cache.get("%s:%s" % (tube_id, 11))["thumb_alt_price"]

        # 주문
        ask_order_id = bithumb_manager.ask(currencypair, ask_alt_amt, thumb_alt_price)

        thumb_btc_ticker = bithumb_manager.get_ticker(CurrencyPair(exchange.symbol.Currency('BTC'),
                                                                   exchange.symbol.Currency('KRW')))
        thumb_btc_price = int(thumb_btc_ticker[0]['close'])
        thumb_alt_value = Decimal(thumb_alt_price / thumb_btc_price).quantize(Decimal('.00000001'), rounding=ROUND_DOWN)

        trex_alt_ticker = bittrex_manager.get_ticker(CurrencyPair(ask_alt_code, exchange.symbol.Currency('BTC')))
        trex_alt_value = trex_alt_ticker[0]['close']

        tube_step = 16
        executed_time = datetime.now()

        # redis
        set_key = "%s:%s" % (tube_id, tube_step)
        set_value = {"tube_id": tube_id,
                     "tube_step": tube_step,
                     "executed_time": executed_time,
                     "ask_alt_code": ask_alt_code,
                     "ask_alt_amt": ask_alt_amt,
                     "ask_order_id": ask_order_id,
                     "thumb_btc_price": thumb_btc_price,
                     "thumb_alt_price": thumb_alt_price,
                     "thumb_alt_value": thumb_alt_value,
                     "trex_alt_value": trex_alt_value,
                     "price": int(Decimal(thumb_alt_price) * ask_alt_amt),
                     "desc": "Starting Asking in Bithumb...",
                     "celery_checked": False}
        cache.set(set_key, set_value, timeout=None)

        # set_step_now(tube_id, tube_step) # celery check_orderbook() 메소드가 할 것임

    #17 ask 완료_bithumb
    def bithumb_sell_complete(self, tube_id):
        step_val = cache.get(tube_id + ":" + str(17))
        if step_val is not None:
            if step_val['celery_checked'] is True:
                return False

        ask_alt_code = get_cache_value(tube_id, 16, "ask_alt_code")
        #thumb_alt_price = get_cache_value(tube_id, 16, "thumb_alt_price")
        ask_alt_amt = get_cache_value(tube_id, 16, "ask_alt_amt")
        step_15_et = get_cache_value(tube_id, 15, "executed_time")

        currencypair = CurrencyPair(ask_alt_code, exchange.symbol.Currency('KRW'))
        r = bithumb_manager.get_order_history(currencypair)
        match = list(filter(lambda history: history['date'] > step_15_et and history['type'] == 'ask', r))
        amount = Decimal(0)
        total = Decimal(0)
        for h in match:
            amount = amount + h["amount"]
            total = total + h["price"] * h["amount"]
        thumb_alt_price = (total / amount).quantize(Decimal('0.00000001'), rounding=ROUND_DOWN)

        msg = "빗썸에서 %s 매도 체결.\n가격 : %d원, 수량 : %.4f, 총액 : %d원" % \
              (ask_alt_code, thumb_alt_price, ask_alt_amt,
               int(thumb_alt_price * ask_alt_amt))
        telegram_handler.alert_admin(msg)

        price = thumb_alt_price * ask_alt_amt

        tube_step = 17
        executed_time = datetime.now()

        # redis
        set_key = "%s:%s" % (tube_id, tube_step)
        set_value = {"tube_id": tube_id,
                     "tube_step": tube_step,
                     "executed_time": executed_time,
                     "price": price,
                     "desc": "Ask Complete in Bithumb",
                     "celery_checked": False}
        cache.set(set_key, set_value, timeout=None)

        set_step_now(tube_id, tube_step)

    #18 (모든 단계 종료) 이후
    def complete(self, tube_id):
        thumb_alt_price = get_cache_value(tube_id, 16, "thumb_alt_price")
        ask_alt_amt = get_cache_value(tube_id, 16, "ask_alt_amt")

        final_price = int(Decimal(thumb_alt_price)
                          * ask_alt_amt
                          * (Decimal('1.0') - Decimal(str(global_preferences['tube_bithumbTransactionFee'])) * Decimal('0.01')))

        # redis
        tube_step = 18
        executed_time = datetime.now()
        set_key = "%s:%s" % (tube_id, tube_step)
        set_value = {"tube_id": tube_id,
                     "tube_step": tube_step,
                     "executed_time": executed_time,
                     "final_price": final_price,
                     "price": final_price,
                     "desc": "Closed Tube",
                     "celery_checked": False}
        cache.set(set_key, set_value, timeout=None)

        print("before redis->mysql")

        # redis -> mysql
        tm = tube_manager.TubeManager()
        result = tm.reg_rdb(tube_id, 10)
        if result:
            # redis data 삭제
            for i in range(1, 19):
                cache.delete("%s:%s" % (tube_id, i))
            # tube_info['step_now'] 0으로 리셋
            set_step_now(tube_id, 0)

        cache.delete("tube_info")

        msg = "튜브 진행이 완료되었습니다.\nTube ID : %s, 최종 금액 : %s원" % (tube_id, final_price)
        telegram_handler.alert_admin(msg)

    def cancel(self, tube_id, tube_step):
        if tube_step == 1 or tube_step == 2:
            currencypair = CurrencyPair(exchange.symbol.Currency('BTC'), exchange.symbol.Currency('KRW'))
            bithumb_manager.cancel(tube_id, currencypair, 'bid')
        elif tube_step == 3:
            bid_order_id = get_cache_value(tube_id, 3, "bid_order_id")
            bid_alt_code = get_cache_value(tube_id, 3, "bid_alt_code")
            currencypair = CurrencyPair(bid_alt_code, exchange.symbol.Currency('KRW'))
            bithumb_manager.cancel(bid_order_id, currencypair, 'bid')
        elif tube_step == 8:
            ask_order_id = get_cache_value(tube_id, 8, "ask_order_id")
            ask_alt_code = get_cache_value(tube_id, 8, "ask_alt_code")
            currencypair = CurrencyPair(ask_alt_code, exchange.symbol.Currency('BTC'))
            bittrex_manager.cancel(ask_order_id, currencypair, 'ask')
        elif tube_step == 11:
            bid_order_id = get_cache_value(tube_id, 11, "bid_order_id")
            bid_alt_code = get_cache_value(tube_id, 11, "bid_alt_code")
            currencypair = CurrencyPair(bid_alt_code, exchange.symbol.Currency('BTC'))
            bittrex_manager.cancel(bid_order_id, currencypair, 'bid')
        elif tube_step == 16:
            ask_order_id = get_cache_value(tube_id, 16, "ask_order_id")
            ask_alt_code = get_cache_value(tube_id, 16, "ask_alt_code")
            currencypair = CurrencyPair(ask_alt_code, exchange.symbol.Currency('BTC'))
            bithumb_manager.cancel(ask_order_id, currencypair, 'ask')

        tm = tube_manager.TubeManager()
        tm.reg_rdb(tube_id, 10, True)

        for i in range(1, 19):
            cache.delete("%s:%s" % (tube_id, i))
        set_step_now(tube_id, 0)

        cache.delete("tube_info")

        msg = "튜브 진행을 취소하였습니다.\nTube ID : %s, Tube Step : %s" % (tube_id, tube_step)
        telegram_handler.alert_admin(msg)
