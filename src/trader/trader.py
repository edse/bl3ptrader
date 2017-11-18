import hmac
import json
import urllib
import base64
import hashlib
import requests
from django.conf import settings
from .storage import Storage
from .base import *  # noqa


class Trader(object):

    def get_balance(self):
        return self.call('GENMKT/money/info', {})

    def get_sell_amount(self, price):
        balance = self.get_balance()
        available = balance['data']['wallets']['BTC']['available']['value_int']

        if available < settings.EXCHANGES['BL3P']['min_sell_value']:
            return 0

        return int(available)

    def get_buy_amount(self, price):
        balance = self.get_balance()
        available = balance['data']['wallets']['EUR']['available']['value_int']

        if available < settings.EXCHANGES['BL3P']['min_buy_value']:
            return 0

        return int(int(available) / price)

    def store_trade(self, params):
        logger.debug('Trade: %s', params)

        Storage.store([{
            'measurement': 'TRADE',
            'tags': {
                'type': params['type']
            },
            'fields': params
        }])

    def buy(self, price, soft_run=True):
        amount = self.get_buy_amount(price * 100000)
        if amount <= 0:
            return False

        params = {
            'type': 'bid',
            'amount_int': amount,
            'price_int': price,
            'fee_currency': 'BTC'
        }
        self.store_trade(params)

        if soft_run:
            return True

        return self.call('BTCEUR/money/order/add', params)

    def sell(self, price):
        amount = self.get_sell_amount(price * 100000)
        if amount <= 0:
            return False

        params = {
            'type': 'ask',
            'amount_int': amount,
            'price_int': price,
            'fee_currency': 'BTC'
        }
        self.store_trade(params)

        if soft_run:
            return True

        return self.call('BTCEUR/money/order/add', params)

    def get_headers(self, path, params):
        post_data = urllib.urlencode(params)
        body = '%s%c%s' % (path, 0x00, post_data)
        headers = {
            'Rest-Key': settings.EXCHANGES['BL3P']['private']['public_key'],
            'Rest-Sign': self.get_signature(body),
        }
        return headers

    def get_signature(self, body):
        return base64.b64encode(
            hmac.new(
                base64.b64decode(
                    settings.EXCHANGES['BL3P']['private']['private_key']
                ),
                body,
                hashlib.sha512
            ).digest()
        )

    def execute(self, path, params, headers, soft_run=True):
        response = requests.post(path, data=params, headers=headers)
        if response.status_code != 200:
            logger.exception('unexpected response: %s%s' % response.status_code, response.content)
            return False

        logger.debug('Response:')
        logger.debug(response.content)

        return json.loads(response.content)

    def call(self, path, params):
        fullpath = settings.EXCHANGES['BL3P']['private']['url'] + path
        headers = self.get_headers(path, params)

        # execute call
        return self.execute(
            path=fullpath,
            params=params,
            headers=headers
        )
