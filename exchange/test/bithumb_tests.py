import unittest

from decimal import Decimal

import time

import os

from exchange.symbol import CurrencyPair, Currency

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "Decryptous.Decryptous.settings")
import django
django.setup()

from exchange.manager.bithumb import BithumbManager


class BithumbManagerTestCase(unittest.TestCase):
    def setUp(self):
        self.bithumb_manager = BithumbManager()

    def test_get_ticker_all(self):
        r = self.bithumb_manager.get_ticker()
        print(r)
        self.assertIsNotNone(r)

    def test_get_ticker_eth(self):
        cp = CurrencyPair(Currency('ETH'), Currency('KRW'))
        r = self.bithumb_manager.get_ticker(cp)
        print(r)
        self.assertIsNotNone(r)

    def test_get_balance_all(self):
        r = self.bithumb_manager.get_balance()
        print(r)
        self.assertIsNotNone(r)

    def test_get_balance_eth(self):
        r = self.bithumb_manager.get_balance(Currency('ETH'))
        print(r)
        self.assertIsNotNone(r)

    def test_get_address_btc(self):
        r = self.bithumb_manager.get_address(Currency('BTC'))
        self.assertEqual("12yUZMF5gXR3KnY1wWh7Rc8qrDhCcvDKf2", r['address'])

    def test_get_address_eth(self):
        r = self.bithumb_manager.get_address(Currency('ETH'))
        self.assertEqual("0x8709719535029b7cd590ab8fc219fde2483b537b", r['address'])

    def test_get_myorder_eth(self):
        r = self.bithumb_manager.get_myorder(CurrencyPair(Currency('ETH'), Currency('KRW')))
        print(r)
        self.assertIsNotNone(r)

    def test_get_order_history_eth(self):
        r = self.bithumb_manager.get_order_history(CurrencyPair(Currency('ETH'), Currency('KRW')))
        print(r)
        self.assertIsNotNone(r)

    def test_get_deposit_history_eth(self):
        r = self.bithumb_manager.get_deposit_history(Currency('ETH'))
        print(r)
        self.assertIsNotNone(r)

    def test_get_withdrawal_history_eth(self):
        r = self.bithumb_manager.get_withdrawal_history(Currency('ETH'))
        print(r)
        self.assertIsNotNone(r)

    def test_bid_and_cancel_xrp(self):
        ticker = self.bithumb_manager.get_ticker(CurrencyPair(Currency('XRP'), Currency('KRW')))
        close = ticker[0]['close']

        order_id = self.bithumb_manager.bid(CurrencyPair(Currency('XRP'), Currency('KRW')), 10,
                                            int(Decimal(close) * Decimal(0.2)))
        self.assertIsNotNone(order_id)

        time.sleep(3)

        cancel = self.bithumb_manager.cancel(order_id, CurrencyPair(Currency('XRP'), Currency('KRW')), 'bid')
        self.assertTrue(cancel)

    def test_ask_and_cancel_xrp(self):
        ticker = self.bithumb_manager.get_ticker(CurrencyPair(Currency('XRP'), Currency('KRW')))
        close = ticker[0]['close']

        order_id = self.bithumb_manager.ask(CurrencyPair(Currency('XRP'), Currency('KRW')), 10,
                                            int(Decimal(close) * Decimal(1.8)))
        self.assertIsNotNone(order_id)

        time.sleep(3)

        cancel = self.bithumb_manager.cancel(order_id, CurrencyPair(Currency('XRP'), Currency('KRW')), 'ask')
        self.assertTrue(cancel)

    def test_bid_qtum(self):
        r = self.bithumb_manager.bid(CurrencyPair(Currency('QTUM'), Currency('KRW')), 1, 3600)
        print(r)

    def test_bid_xrp(self):
        r = self.bithumb_manager.bid(CurrencyPair(Currency('XRP'), Currency('KRW')), 10, 150)
        print(r)

    def test_set_data_to_redis(self):
        from django.core.cache import cache
        cache.set("test", "test-value!!!", timeout=None)
        # print(cache.get("1523883935679831:1"))
        print("good")
