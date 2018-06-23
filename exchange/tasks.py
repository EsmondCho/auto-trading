from django.core.cache import cache

from celery import shared_task

from exchange.manager.bithumb import BithumbManager
from exchange.manager.bittrex import BittrexManager

from exchange.models import WalletAddress, WithdrawalFee
from decimal import Decimal, ROUND_DOWN
import time
from datetime import datetime, timedelta

@shared_task
def echo(name):
    return "hi!! " + str(name)


@shared_task
def check_orderbook():
    tube_info = cache.get("tube_info")
    if tube_info is None:
        return False
    # tube_id = tube_info['tube_id']
    # step_now = tube_info['step_now']

    bithumb_manager = BithumbManager()
    bithumb_orderbook = cache.get("bithumb")
    if bithumb_orderbook is not None:
        if len(bithumb_orderbook) > 0:
            for order in bithumb_orderbook:

                time.sleep(5)

                tube_info = cache.get("tube_info")
                tube_id = tube_info['tube_id']
                step_now = tube_info['step_now']

                my_orders = bithumb_manager.get_myorder(order["currencypair"])

                if ((step_now == 2 and cache.get("%s:%s" % (tube_id, 3))["bid_order_id"] == order["order_id"]) or (step_now == 15 and cache.get("%s:%s" % (tube_id, 16))["ask_order_id"] == order["order_id"])) and len(my_orders) == 0:
                    # delete in redis
                    bithumb_orderbook.remove(order)
                    cache.set("bithumb", bithumb_orderbook, timeout=None)
                    # update tube_info['step_now']
                    if step_now == 2:
                        step_now = 3
                        tube_info = {"tube_id": tube_id, "step_now": step_now}
                        cache.set("tube_info", tube_info, timeout=None)
                        return True
                    elif step_now == 15:
                        step_now = 16
                        tube_info = {"tube_id": tube_id, "step_now": step_now}
                        cache.set("tube_info", tube_info, timeout=None)
                        return True

    bittrex_manager = BittrexManager()
    bittrex_orderbook = cache.get("bittrex")
    if bittrex_orderbook is not None:
        if len(bittrex_orderbook) > 0:
            for order in bittrex_orderbook:

                time.sleep(5)

                tube_info = cache.get("tube_info")
                tube_id = tube_info['tube_id']
                step_now = tube_info['step_now']

                my_orders = bittrex_manager.get_myorder(order["currencypair"])
                if ((step_now == 7 and cache.get("%s:%s" % (tube_id, 8))["ask_order_id"] == order["order_id"]) or (step_now == 10 and cache.get("%s:%s" % (tube_id, 11))["bid_order_id"] == order["order_id"])) and len(my_orders) == 0:
                    # delete in redis
                    bittrex_orderbook.remove(order)
                    cache.set("bittrex", bittrex_orderbook, timeout=None)
                    # update tube_info['step_now']
                    if step_now == 7:
                        step_now = 8
                        tube_info = {"tube_id": tube_id, "step_now": step_now}
                        cache.set("tube_info", tube_info, timeout=None)
                        return True
                    elif step_now == 10:
                        step_now = 11
                        tube_info = {"tube_id": tube_id, "step_now": step_now}
                        cache.set("tube_info", tube_info, timeout=None)
                        return True
    return False

@shared_task
def check_account():
    tube_info = cache.get("tube_info")
    if tube_info is None:
        return False
    tube_id = tube_info['tube_id']
    step_now = tube_info['step_now']

    bithumb_manager = BithumbManager()
    bittrex_manager = BittrexManager()

    if step_now == 4:
        key = tube_id + ":" + str(5)
        val = cache.get(key)

        thumb_out_alt_code = val["thumb_out_alt_code"]
        thumb_out_alt_amt = val["thumb_out_alt_amt"]

        r = bithumb_manager.get_withdrawal_history(thumb_out_alt_code)
        real_withdrawal_list = []

        for dic in r:
            started_time = cache.get(tube_id+":"+str(1))['executed_time']
            if dic['date'] + timedelta(hours=9) > started_time:
                real_withdrawal_list.append(dic)

        real_withdrawal_list.sort(key=lambda x: x['date'])

        withdrawal_fee = WithdrawalFee.objects.filter(exchange__id=1, currency__symbol=thumb_out_alt_code).get().fee
        # 출금 완료
        print("======= step4 =======")
        print(real_withdrawal_list)
        print(withdrawal_fee)
        print(thumb_out_alt_amt)
        print("=====================")
        if len(real_withdrawal_list) > 0 and thumb_out_alt_amt.compare(real_withdrawal_list[-1]['amount'] - withdrawal_fee) == 0:
            # update tube_info['step_now']
            step_now = 5
            tube_info = {"tube_id": tube_id, "step_now": step_now}
            cache.set("tube_info", tube_info, timeout=None)
            return True

    elif step_now == 5:
        key = tube_id + ":" + str(5)
        val = cache.get(key)
        trex_in_alt_code = val["thumb_out_alt_code"]
        trex_in_alt_amt = val["thumb_out_alt_amt"]

        r = bittrex_manager.get_deposit_history(trex_in_alt_code)
        real_deposit_list = []

        for dic in r:
            started_time = cache.get(tube_id+":"+str(1))['executed_time']
            if dic['date'] + timedelta(hours=9) > started_time:
                real_deposit_list.append(dic)

        real_deposit_list.sort(key=lambda x: x['date'])

        if len(real_deposit_list) > 0:
            print("====== step5  ======")
            print(real_deposit_list)
            print(trex_in_alt_amt)
            print(float(real_deposit_list[-1]['amount']))
            print(float(real_deposit_list[-1]['amount']) == float(trex_in_alt_amt))
            print("====================")
        # 입금 완료
        # 출금 후 bithumb에 잔액 조금 남는 경우를 대비
        if len(real_deposit_list) > 0 and abs(float(real_deposit_list[-1]['amount']) - float(trex_in_alt_amt)) < 0.01:
            # 실제 bittrex에 들어온 alt amount를 redis에 반영
            if float(real_deposit_list[-1]['amount']) != float(trex_in_alt_amt):
                val["thumb_out_alt_amt"] = real_deposit_list[-1]['amount']
                cache.set(key, val, timeout=None)

            # update tube_info['step_now']
            step_now = 6
            tube_info = {"tube_id": tube_id, "step_now": step_now}
            cache.set("tube_info", tube_info, timeout=None)
            return True

    elif step_now == 12:
        key = tube_id + ":" + str(11)
        val = cache.get(key)

        trex_out_alt_code = val["bid_alt_code"]
        bid_alt_amt = val["bid_alt_amt"]
        withdrawal_fee = WithdrawalFee.objects.filter(exchange__id=2, currency__symbol=trex_out_alt_code).get().fee
        trex_out_alt_code = val["bid_alt_code"]
        trex_out_alt_amt = bid_alt_amt - withdrawal_fee

        r = bittrex_manager.get_withdrawal_history(trex_out_alt_code)
        real_withdrawal_list = []

        for dic in r:
            started_time = cache.get(tube_id+":"+str(1))['executed_time']
            if dic['date'] + timedelta(hours=9) > started_time:
                real_withdrawal_list.append(dic)

        real_withdrawal_list.sort(key=lambda x: x['date'])

        print("====== step12 ======")
        print(real_withdrawal_list)
        print(withdrawal_fee)
        print(trex_out_alt_amt)
        print("====================")
        # 출금 완료
        if len(real_withdrawal_list) > 0 and trex_out_alt_amt.compare(r[0]['amount']) == 0:
            # update tube_info['step_now']
            step_now = 13
            tube_info = {"tube_id": tube_id, "step_now": step_now}
            cache.set("tube_info", tube_info, timeout=None)
            return True

    elif step_now == 13:
        key = tube_id + ":" + str(13)
        val = cache.get(key)

        thumb_in_alt_code = val["trex_out_alt_code"]
        thumb_in_alt_amt = val["trex_out_alt_amt"].quantize(Decimal('.000001'), rounding=ROUND_DOWN)

        r = bithumb_manager.get_deposit_history(thumb_in_alt_code)
        real_deposit_list = []

        for dic in r:
            started_time = cache.get(tube_id + ":" + str(1))['executed_time']
            if dic['date'] + timedelta(hours=9) > started_time:
                real_deposit_list.append(dic)

        real_deposit_list.sort(key=lambda x: x['date'])
        if len(real_deposit_list) > 0:
            print("====== step13 ======")
            print(real_deposit_list)
            print(thumb_in_alt_amt)
            print(float(real_deposit_list[-1]['amount']))
            print("====================")
        # 입금 완료
        # 출금 후 bittrex에 잔액 조금 남는 경우를 대비
        if len(real_deposit_list) > 0 and abs(float(real_deposit_list[-1]['amount']) - float(thumb_in_alt_amt)) < 0.01:
            # 실제 bithumb에 들어온 alt amount를 redis에 반영
            if float(real_deposit_list[-1]['amount']) != float(thumb_in_alt_amt):
                val["thumb_out_alt_amt"] = real_deposit_list[-1]['amount']
                cache.set(key, val, timeout=None)
            # update tube_info['step_now']
            step_now = 14
            tube_info = {"tube_id": tube_id, "step_now": step_now}
            cache.set("tube_info", tube_info, timeout=None)
            return True

    return False
