from django.shortcuts import render
from django.http import HttpResponse
from django.core.cache import cache
from django.forms.models import model_to_dict
from .models import *
from exchange.models import Currency
from datetime import datetime
import json


def fetch_data(request):
    tube_info = cache.get("tube_info")
    if tube_info is not None:
        tube_id = tube_info['tube_id']
        step_now = int(tube_info['step_now'])

        step_info_list = []
        for i in range(0, step_now):
            key = tube_id + ":" + str(i+1)
            val = cache.get(key)
            val = str(val)
            # val['executed_time'] = str(val['executed_time'])
            # val['thumb_out_alt_code'] = str(val['thumb_out_alt_code'])
            # val['thumb_out_alt_amt'] = str(val['thumb_out_alt_amt'])
            step_info_list.append(val)

        dic = {tube_id: step_info_list}
        return HttpResponse(json.dumps(dic), content_type='application/json', status=200)

    dic = {'return': False}
    return HttpResponse(json.dumps(dic), content_type='application/json', status=200)


def get_history_summary(request):
    query_dict = request.GET
    page = query_dict.get("page")
    if page is None:
        events = EventLog.objects.order_by("time_stamp", "tube_id", "stage")
    else:
        if int(page) < 1:
            return False

        page = int(page)
        tube_id_list_all = list(EventLog.objects.values_list('tube_id', flat=True).distinct())
        tube_id_list_all.reverse()
        tube_id_list_selected = tube_id_list_all[(page-1)*10:page*10]
        if len(tube_id_list_selected) < 1:
            dic = {"message": "page out of range"}
            return HttpResponse(json.dumps(dic), content_type='application/json', status=400)

        events = EventLog.objects.filter(tube_id__in=tube_id_list_selected)
        history_list, tube_id, summary_dict, first = [], "", {}, True
        for e in events:
            if tube_id != e.tube_id:
                if first is False:
                    history_list.append(summary_dict)

                first = False
                summary_dict = {}
                tube_id = e.tube_id
                summary_dict['tube_id'] = tube_id
                summary_dict['stages'] = []

            dic = {"stage": e.stage, "event": e.event, "price": e.price,\
                   "time_stamp": str(e.time_stamp)[0:19]}
            summary_dict['stages'].append(dic)
        if summary_dict is not {}:
            history_list.append(summary_dict)

        for history in history_list:
            taken_time = str(datetime.strptime(history['stages'][-1]['time_stamp'], '%Y-%m-%d %H:%M:%S')\
                        - datetime.strptime(history['stages'][0]['time_stamp'], '%Y-%m-%d %H:%M:%S'))
            end_time = history['stages'][-1]['time_stamp']
            if history['stages'][-1]['stage'] == 10 and history['stages'][-1]['event'] != 6:
                status = "complete"
            else:
                status = "error"

            if status == "complete":
                profit = history['stages'][-1]['price'] - history['stages'][0]['price']
            else:
                profit = 0

            if profit == 0:
                profit_per = 0
            elif status == "error":
                profit_per = 0
            else:
                profit_per = round(profit / history['stages'][0]['price'], 3)

            history['tube_time'] = taken_time
            history['profit'] = profit
            history['profit_per'] = profit_per
            history['end_time'] = end_time
            history['status'] = status
            history.pop('stages')

        history_list.reverse()
        history = {"num_of_tube": len(tube_id_list_all), "history_tube_list": history_list}
        return HttpResponse(json.dumps(history), content_type='application/json', status=200)


def get_history(request, tid):
    e_list = EventLog.objects.filter(tube_id=tid)
    step_list = []
    for e in e_list:
        tube_id = e.tube_id
        stage = e.stage
        price = e.price
        time = str(e.time_stamp)
        eid = e.eventinfo_id
        type = e.event

        if stage == 1:
            step_list.append(step_dict(tube_id, stage, "init", "", "", 0, 0, price, time))
        elif stage == 2:
            order = OrderInfo.objects.get(id=eid)
            coin_name = Currency.objects.get(id=order.market_counter.id).symbol
            step_list.append(step_dict(tube_id, stage, "bid", 1, coin_name, order.coin_amt, order.value, price, time))
        elif stage == 3:
            transfer = TransferInfo.objects.get(id=eid)
            coin_name = Currency.objects.get(id=transfer.currency_id).symbol
            step_list.append(step_dict(tube_id, stage, "withdrawal", 1, coin_name, transfer.coin_amt, "", price, time))
        elif stage == 4:
            transfer = TransferInfo.objects.get(id=eid)
            coin_name = Currency.objects.get(id=transfer.currency_id).symbol
            step_list.append(step_dict(tube_id, stage, "deposit", 2, coin_name, transfer.coin_amt, "", price, time))
        elif stage == 5:
            order = OrderInfo.objects.get(id=eid)
            coin_name = Currency.objects.get(id=order.market_counter.id).symbol
            step_list.append(step_dict(tube_id, stage, "ask", 2, coin_name, order.coin_amt, order.value, price, time))
        elif stage == 6:
            order = OrderInfo.objects.get(id=eid)
            coin_name = Currency.objects.get(id=order.market_counter.id).symbol
            step_list.append(step_dict(tube_id, stage, "bid", 2, coin_name, order.coin_amt, order.value, price, time))
        elif stage == 7:
            transfer = TransferInfo.objects.get(id=eid)
            coin_name = Currency.objects.get(id=transfer.currency_id).symbol
            step_list.append(step_dict(tube_id, stage, "withdrawal", 2, coin_name, transfer.coin_amt, "", price, time))
        elif stage == 8:
            transfer = TransferInfo.objects.get(id=eid)
            coin_name = Currency.objects.get(id=transfer.currency_id).symbol
            step_list.append(step_dict(tube_id, stage, "deposit", 1, coin_name, transfer.coin_amt, "", price, time))
        elif stage == 9:
            order = OrderInfo.objects.get(id=eid)
            coin_name = Currency.objects.get(id=order.market_counter.id).symbol
            step_list.append(step_dict(tube_id, stage, "ask", 1, coin_name, order.coin_amt, order.value, price, time))
        elif stage == 10:
            step_list.append(step_dict(tube_id, stage, "close", "", "", 0, 0, price, time))
        if type == 7:
            step_list[-1]['event'] = 'cancel'
    return HttpResponse(json.dumps(step_list, default=json_default), content_type='application/json', status=200)


def step_dict(*args):
    return {"tube_id": args[0], "stage": args[1], "event": args[2], "exchange": args[3],\
            "coin_name": args[4], "coin_amt": args[5], "coin_value": args[6], "price": args[7],\
            "time_stamp": args[8]}


def json_default(value):
    return str(value)
