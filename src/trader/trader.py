from datetime import datetime
from django.conf import settings
from . import watcher as Watcher
from .client import Bl3p
from .storage import Storage
from .models import Trade
from .analyser import Analyser
from .base import *  # noqa


class Trader(object):

    def __init__(self):
        self.client = Bl3p()
        self.analyser = Analyser()
        self.watcher = Watcher

    def start(self):
        self.watcher.run()

    def start_ticker(self):
        self.watcher.run_ticker(self)

    def start_trader(self):
        self.watcher.run_trader(self)

    def analyse(self, trend_result):
        trader.take_action(
            trend=trend_result.trend,
            current=trend_result.current
        )

    def get_sell_amount(self):
        balance = self.client.get_balance()
        available = int(balance['data']['wallets']['BTC']['available']['value_int'])

        if available < settings.EXCHANGES['BL3P']['min_sell_value']:
            return 0

        return available

    def get_buy_amount(self, price):
        balance = self.client.get_balance()
        available = balance['data']['wallets']['EUR']['available']['value_int']

        if available < settings.EXCHANGES['BL3P']['min_buy_value']:
            return 0

        return int(float(available) / float(price) * NORM_AMOUNT)

    def store_trade(self, params):
        logger.debug('Trade: %s', params)

        amount = float(params['amount_int']) / NORM_AMOUNT
        price = float(params['price_int']) / NORM_PRICE
        fee = float(settings.EXCHANGES['BL3P']['trade_fee'])
        total = (price * amount) + (((price * amount) / 100) * fee)

        # Influx
        stored = Storage.store([{
            'measurement': 'TRADE',
            'tags': {
                'asset': params['type'],
            },
            'fields': {
                'price': price,
                'amount': amount,
                'trend': 10 if params['type'] == 'bid' else -10
            }
        }])

        # Django
        Trade.objects.create(
            amount=amount,
            price=price,
            total=total,
            fee=fee,
            type=Trade.BUY if params['type'] == 'bid' else Trade.SELL
        )

        logger.debug('Trade stored: %s', stored)

    def buy(self, price):
        price = int(price * NORM_PRICE)
        amount = self.get_buy_amount(price)
        params = {
            'type': 'bid',
            'amount_int': amount,
            'price_int': price,
            'fee_currency': 'BTC'
        }

        if amount <= 0:
            return False

        self.store_trade(params)
        self.client.add_order(params)

    def sell(self, price):
        price = int(price * NORM_PRICE)
        amount = self.get_sell_amount()
        params = {
            'type': 'ask',
            'amount_int': amount,
            'price_int': price,
            'fee_currency': 'BTC'
        }

        if amount <= 0:
            return False

        self.store_trade(params)
        self.client.add_order(params)

    def take_action(self, trend, current):
        logger.setLevel(logging.ERROR)
        logger.debug('%s: %s', str(datetime.now()), trend)

        fee = float(settings.EXCHANGES['BL3P']['trade_fee'])
        cust = current['price'] + ((current['price'] / 100) * fee)
        last_order = Trade.objects.all().last()

        if trend == 10:
            logger.debug('Trend: 10 >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>')
            if last_order:
                if settings.EXCHANGES['BL3P']['intercalate_trade']:
                    # last order must be a sell
                    if last_order.type == Trade.BUY:
                        logger.exception('Trying to buy after a buy with intercalate_trade set to true!')
                        return False

                if settings.EXCHANGES['BL3P']['safe_trade']:
                    # check if the buy price + fees is cheaper than the last sell
                    if cust >= last_order.price:
                        logger.exception('Trying to buy for a higher price than the last sell with safe_trade set to true!')
                        logger.exception('Price + fees: %s', cust)
                        logger.exception('Last trade price: %s', last_order.price)
                        return False
            # BUY
            self.buy(current['price'])

        elif trend == -10:
            logger.debug('Trend: -10 >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>')
            if last_order:
                if settings.EXCHANGES['BL3P']['intercalate_trade']:
                    # last order must be a buy
                    if last_order.type == Trade.SELL:
                        logger.exception('Trying to sell after a sell with intercalate_trade set to true!')
                        return False

                if settings.EXCHANGES['BL3P']['safe_trade']:
                    # check if the sell price is higher than the last buy + fees
                    if cust <= last_order.price:
                        logger.exception('Trying to sell for a cheaper price than the last buy with safe_trade set to true!')
                        logger.exception('Price + fees: %s', cust)
                        logger.exception('Last trade price: %s', last_order.price)
                        return False
            # SELL
            self.sell(current['price'])
