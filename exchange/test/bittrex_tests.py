import unittest

from decimal import Decimal

import time

import os

from exchange.symbol import CurrencyPair, Currency

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "Decryptous.Decryptous.settings")
import django
django.setup()

from exchange.manager.bittrex import BittrexManager


class BittrexManagerTestCase(unittest.TestCase):
    def setUp(self):
        self.bittrex_manager = BittrexManager()

    def test_get_ticker_all(self):
        r = self.bittrex_manager.get_ticker()
        print(r)
        self.assertIsNotNone(r)

    def test_get_ticker_eth(self):
        r = self.bittrex_manager.get_ticker(CurrencyPair(Currency('ETH'), Currency('BTC')))
        print(r)
        self.assertIsNotNone(r)

    def test_get_balance_all(self):
        r = self.bittrex_manager.get_balance()
        print(r)
        self.assertIsNotNone(r)

    def test_get_balance_eth(self):
        r = self.bittrex_manager.get_balance(Currency('ETH'))
        print(r)
        self.assertIsNotNone(r)

    def test_get_address_btc(self):
        r = self.bittrex_manager.get_address(Currency('BTC'))
        self.assertEqual("1EmDhHaYZZ4zUJqE3yBMgZTjPaPeg2Qfme", r['address'])

    def test_get_address_eth(self):
        r = self.bittrex_manager.get_address(Currency('ETH'))
        self.assertEqual("0x6a8145a878060d1dab3000913273fc0ab54cc998", r['address'])

    def test_get_myorder_eth(self):
        r = self.bittrex_manager.get_myorder(CurrencyPair(Currency('ETH'), Currency('BTC')))
        print(r)
        self.assertIsNotNone(r)

    def test_get_order_history_eth(self):
        r = self.bittrex_manager.get_order_history(CurrencyPair(Currency('ETH'), Currency('BTC')))
        print(r)
        self.assertIsNotNone(r)

    def test_get_deposit_history_eth(self):
        r = self.bittrex_manager.get_deposit_history(Currency('ETH'))
        print(r)
        self.assertIsNotNone(r)

    def test_get_withdrawal_history_eth(self):
        r = self.bittrex_manager.get_withdrawal_history(Currency('ETH'))
        print(r)
        self.assertIsNotNone(r)

    def test_bid_and_cancel_xrp(self):
        ticker = self.bittrex_manager.get_ticker(CurrencyPair(Currency('XRP'), Currency('BTC')))
        close = ticker[0]['close']

        order_id = self.bittrex_manager.bid(CurrencyPair(Currency('XRP'), Currency('BTC')),
                                            10, Decimal(close) * Decimal(0.2))
        self.assertIsNotNone(order_id)

        time.sleep(3)

        cancel = self.bittrex_manager.cancel(order_id)
        self.assertTrue(cancel)

    def test_ask_and_cancel_xrp(self):
        ticker = self.bittrex_manager.get_ticker(CurrencyPair(Currency('XRP'), Currency('BTC')))
        close = ticker[0]['close']

        order_id = self.bittrex_manager.ask(CurrencyPair(Currency('XRP'), Currency('BTC')),
                                            10, Decimal(close) * Decimal(1.8))
        self.assertIsNotNone(order_id)

        time.sleep(3)

        cancel = self.bittrex_manager.cancel(order_id)
        self.assertTrue(cancel)

    # def test_bid_qtum(self):
    #     r = self.bittrex_manager.bid(CurrencyPair(Currency('QTUM'), Currency('KRW')), 1, 3600)
    #     print(r)
    #
    # def test_bid_xrp(self):
    #     r = self.bittrex_manager.bid(CurrencyPair(Currency('XRP'), Currency('KRW')), 10, 150)
    #     print(r)
