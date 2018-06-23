from datetime import datetime

import exchange
from exchange.models import Exchange
from tube.models import EventLog, ErrorInfo, TransferInfo, OrderInfo
from tube import process
from django.core.cache import cache
from tube import telegram_handler


class TubeManager:
    def __init__(self):
        self.pc = process.Process()

    def handleErr(self, tube_id, stage, ex):
        print(ex)

        cache.delete("tube_info")

        msg = "[Error] Tube ID : %s, Stage : %d\n%s" % (tube_id, stage, str(ex))
        telegram_handler.alert_admin(msg)

        self.reg_rdb(tube_id, stage)

        ei = ErrorInfo(desc=str(ex))
        ei.save()

        final_price = 0 #TODO 0이 아니라 마지막 step의 추정 가격을 가져올 것
        if stage > 1:
            el = EventLog.objects.filter(tube_id=tube_id).order_by('-stage').all()[:1].get()
            final_price = el.price
        EventLog(tube_id=tube_id, stage=stage, event=6, price=final_price, time_stamp=datetime.now(), eventinfo_id=ei.id)\
            .save()

        #redis truncate
        for i in range(1, 19):
            cache.delete("%s:%s" % (tube_id, i))

        msg = "튜브 진행이 오류로 인해 중단되었습니다.\nTube ID : %s, 최종 금액 : %s" % (tube_id, final_price)
        telegram_handler.alert_admin(msg)

    def reg_rdb(self, tube_id, stage, cancel=False):
        last_stage = 0
        exoccur = False

        try:
            redis_info = []

            for i in range(1, 19):
                redis_info.append(cache.get("%s:%s" % (tube_id, i)))

            if stage > 1:
                #1 init
                EventLog(tube_id=tube_id, stage=1, event=0, price=redis_info[0]["init_price"],
                         time_stamp=redis_info[0]["executed_time"]).save()

                last_stage = 1

            if stage > 2:
                #2 bithumb bid
                oi2 = OrderInfo(order_id=redis_info[2]["bid_order_id"], order_type=0,
                                market_counter=exchange.models.Currency.objects.filter(
                                    symbol=str(redis_info[2]["bid_alt_code"])).get(),
                                market_base=exchange.models.Currency.objects.filter(symbol="KRW").get(),
                                coin_amt=redis_info[2]["bid_alt_amt"],
                                value=redis_info[2]["thumb_alt_price"],
                                exchange=Exchange.objects.filter(name="bithumb").get())
                oi2.save()

                EventLog(tube_id=tube_id, stage=2, event=2,
                         price=int(redis_info[2]["thumb_alt_price"] * redis_info[2]["bid_alt_amt"]),
                         time_stamp=redis_info[3]["executed_time"], eventinfo_id=oi2.id).save()

                last_stage = 2

            if stage > 3:
                #3 bithumb withdrawal
                ti3 = TransferInfo(coin_amt=redis_info[4]["thumb_out_alt_amt"],
                                   src=Exchange.objects.filter(name="bithumb").get(),
                                   dest=Exchange.objects.filter(name="bittrex").get(),
                                   currency=exchange.models.Currency.objects.filter(
                                       symbol=str(redis_info[4]["thumb_out_alt_code"])).get(),
                                   transfer_type=1)
                ti3.save()

                EventLog(tube_id=tube_id, stage=3, event=4,
                         price=int(redis_info[2]["thumb_alt_price"] * redis_info[4]["thumb_out_alt_amt"]),
                         time_stamp=redis_info[5]["executed_time"], eventinfo_id=ti3.id).save()

                last_stage = 3

            if stage > 4:
                #4 bittrex deposit
                ti4 = TransferInfo(coin_amt=redis_info[6]["trex_in_alt_amt"],
                                   src=Exchange.objects.filter(name="bithumb").get(),
                                   dest=Exchange.objects.filter(name="bittrex").get(),
                                   currency=exchange.models.Currency.objects.filter(
                                       symbol=str(redis_info[6]["trex_in_alt_code"])).get(),
                                   transfer_type=0)
                ti4.save()

                EventLog(tube_id=tube_id, stage=4, event=5,
                         price=int(redis_info[2]["thumb_alt_price"] * redis_info[6]["trex_in_alt_amt"]),
                         time_stamp=redis_info[6]["executed_time"], eventinfo_id=ti3.id).save()

                last_stage = 4

            if stage > 5:
                #5 bittrex ask
                oi5 = OrderInfo(order_id=redis_info[7]["ask_order_id"], order_type=1,
                                market_counter=exchange.models.Currency.objects.filter(
                                    symbol=str(redis_info[7]["ask_alt_code"])).get(),
                                market_base=exchange.models.Currency.objects.filter(symbol="BTC").get(),
                                coin_amt=redis_info[7]["ask_alt_amt"],
                                value=redis_info[7]["trex_alt_value"],
                                exchange=Exchange.objects.filter(name="bittrex").get())
                oi5.save()

                EventLog(tube_id=tube_id, stage=5, event=3,
                         price=int(
                             redis_info[7]["trex_alt_value"] * redis_info[7]["ask_alt_amt"] * redis_info[7]["thumb_btc_price"]),
                         time_stamp=redis_info[8]["executed_time"], eventinfo_id=oi5.id).save()

                last_stage = 5

            if stage > 6:
                #6 bittrex bid
                oi6 = OrderInfo(order_id=redis_info[10]["bid_order_id"], order_type=0,
                                market_counter=exchange.models.Currency.objects.filter(
                                    symbol=str(redis_info[10]["bid_alt_code"])).get(),
                                market_base=exchange.models.Currency.objects.filter(symbol="BTC").get(),
                                coin_amt=redis_info[10]["bid_alt_amt"],
                                value=redis_info[10]["trex_alt_value"],
                                exchange=Exchange.objects.filter(name="bittrex").get())
                oi6.save()

                EventLog(tube_id=tube_id, stage=6, event=2,
                         price=int(
                             redis_info[10]["trex_alt_value"] * redis_info[10]["bid_alt_amt"] *
                             redis_info[10]["thumb_btc_price"]),
                         time_stamp=redis_info[11]["executed_time"], eventinfo_id=oi6.id).save()

                last_stage = 6

            if stage > 7:
                #7 bittrex withdrawal
                ti7 = TransferInfo(coin_amt=redis_info[12]["trex_out_alt_amt"],
                                   src=Exchange.objects.filter(name="bittrex").get(),
                                   dest=Exchange.objects.filter(name="bithumb").get(),
                                   currency=exchange.models.Currency.objects.filter(
                                       symbol=str(redis_info[12]["trex_out_alt_code"])).get(),
                                   transfer_type=1)
                ti7.save()

                EventLog(tube_id=tube_id, stage=7, event=4,
                         price=int(redis_info[10]["trex_alt_value"] * redis_info[12]["trex_out_alt_amt"] *
                             redis_info[10]["thumb_btc_price"]),
                         time_stamp=redis_info[13]["executed_time"], eventinfo_id=ti7.id).save()

                last_stage = 7

            if stage > 8:
                #8 bithumb deposit
                ti8 = TransferInfo(coin_amt=redis_info[14]["thumb_in_alt_amt"],
                                   src=Exchange.objects.filter(name="bittrex").get(),
                                   dest=Exchange.objects.filter(name="bithumb").get(),
                                   currency=exchange.models.Currency.objects.filter(
                                       symbol=str(redis_info[14]["thumb_in_alt_code"])).get(),
                                   transfer_type=0)
                ti8.save()

                EventLog(tube_id=tube_id, stage=8, event=5,
                         price=int(redis_info[10]["trex_alt_value"] * redis_info[14]["thumb_in_alt_amt"] *
                             redis_info[10]["thumb_btc_price"]),
                         time_stamp=redis_info[14]["executed_time"], eventinfo_id=ti8.id).save()

                last_stage = 8

            if stage > 9:
                #9 bithumb ask
                oi9 = OrderInfo(order_id=redis_info[15]["ask_order_id"], order_type=1,
                                market_counter=exchange.models.Currency.objects.filter(
                                    symbol=str(redis_info[15]["ask_alt_code"])).get(),
                                market_base=exchange.models.Currency.objects.filter(symbol="KRW").get(),
                                coin_amt=redis_info[15]["ask_alt_amt"],
                                value=redis_info[15]["thumb_alt_price"],
                                exchange=Exchange.objects.filter(name="bithumb").get())
                oi9.save()

                EventLog(tube_id=tube_id, stage=9, event=3,
                         price=int(redis_info[15]["thumb_alt_price"] * redis_info[15]["ask_alt_amt"]),
                         time_stamp=redis_info[16]["executed_time"], eventinfo_id=oi9.id).save()

                last_stage = 9

            if stage >= 10:
                #10 close
                EventLog(tube_id=tube_id, stage=10, event=1, price=redis_info[17]["final_price"],
                         time_stamp=redis_info[17]["executed_time"]).save()

                last_stage = 10
        except Exception as ex:
            exoccur = True

        if cancel:
            EventLog(tube_id=tube_id, stage=last_stage, event=7, price=0, time_stamp=datetime.now()).save()

        return not exoccur

    # 초기금액 입력 & 허매수 & alt 선택 & 허매수 취소 & bid 신청
    def stage1(self):
        try:
            #self.pc.set_init_krw()

            tube_info = cache.get("tube_info")
            #self.pc.select_bithumb_altcoin(tube_info['tube_id'])
            self.pc.bithumb_bid(tube_info['tube_id'])
        except Exception as ex:
            self.handleErr(tube_info['tube_id'], 1, ex)
            return False
        return True

    # bid 채결 완료 & 출금 신청
    def stage2(self):
        try:
            tube_info = cache.get("tube_info")
            self.pc.bithumb_bid_complete(tube_info['tube_id'])
            self.pc.bithumb_withdrawal(tube_info['tube_id'])
        except Exception as ex:
            self.handleErr(tube_info['tube_id'], 2, ex)
            return False
        return True

    # 빗썸 출금 완료
    def stage3(self):
        try:
            tube_info = cache.get("tube_info")
            self.pc.bithumb_withdrawal_complete(tube_info['tube_id'])
        except Exception as ex:
            self.handleErr(tube_info['tube_id'], 3, ex)
            return False
        return True

    # 비트렉스 입금 완료 & BTC ask 신청
    def stage4(self):
        try:
            tube_info = cache.get("tube_info")
            self.pc.bittrex_deposit_complete(tube_info['tube_id'])
            self.pc.bittrex_ask_to_btc(tube_info['tube_id'])
        except Exception as ex:
            self.handleErr(tube_info['tube_id'], 4, ex)
            return False
        return True

    # ask 채결 완료
    def stage5(self):
        try:
            tube_info = cache.get("tube_info")
            self.pc.bittrex_ask_to_btc_complete(tube_info['tube_id'])
        except Exception as ex:
            self.handleErr(tube_info['tube_id'], 5, ex)
            return False
        return True

    # alt 선택은 유저가 직접 메소드 호출 : select_bittrex_altcoin()

    # bid 신청
    def stage6(self):
        try:
            tube_info = cache.get("tube_info")
            self.pc.bittrex_bid(tube_info['tube_id'])
        except Exception as ex:
            self.handleErr(tube_info['tube_id'], 6, ex)
            return False
        return True

    # bid 채결 완료 & 출금 신청
    def stage7(self):
        try:
            tube_info = cache.get("tube_info")
            self.pc.bittrex_bid_complete(tube_info['tube_id'])
            self.pc.bittrex_withdrawal(tube_info['tube_id'])
        except Exception as ex:
            self.handleErr(tube_info['tube_id'], 7, ex)
            return False
        return True

    # 비트렉스 출금 완료
    def stage8(self):
        try:
            tube_info = cache.get("tube_info")
            self.pc.bittrex_withdrawal_complete(tube_info['tube_id'])
        except Exception as ex:
            self.handleErr(tube_info['tube_id'], 8, ex)
            return False
        return True

    # 빗썸 입금 완료 & KRW ask 신청
    def stage9(self):
        try:
            tube_info = cache.get("tube_info")
            self.pc.bithumb_deposit_complete(tube_info['tube_id'])
            self.pc.bithumb_sell(tube_info['tube_id'])
        except Exception as ex:
            self.handleErr(tube_info['tube_id'], 9, ex)
            return False
        return True

    # ask 채결 완료
    def stage10(self):
        try:
            tube_info = cache.get("tube_info")
            self.pc.bithumb_sell_complete(tube_info['tube_id'])
        except Exception as ex:
            self.handleErr(tube_info['tube_id'], 10, ex)
            return False
        return True

    # redis -> mysql 데이터 옮기고 redis 해당 tube 정보 삭제
    def stage11(self):
        try:
            tube_info = cache.get("tube_info")
            self.pc.complete(tube_info['tube_id'])
        except Exception as ex:
            self.handleErr(tube_info['tube_id'], 11, ex)
            return False
        return True
