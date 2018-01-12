from django.conf import settings
import json
import requests
from time import sleep
import websocket

from .storage import Storage
from .base import *  # noqa

websocket.enableTrace(True)

trader = None
ws_trades = None
ws_ticker = None


def get_ticker_path():
    return settings.EXCHANGES['BL3P']['public']['http'] + \
        settings.EXCHANGES['BL3P']['public']['paths']['ticker']


def get_trades_path():
    return settings.EXCHANGES['BL3P']['public']['wss'] + \
        settings.EXCHANGES['BL3P']['public']['paths']['trades']


def parse_trade(message):
    data = json.loads(message)
    price = float(data['price_int']) / NORM_PRICE
    amount = float(data['amount_int']) / NORM_AMOUNT
    return Storage.store([{
        'measurement': 'BTC_EUR',
        'tags': {
            'asset': 'BTC',
            'currency': 'EUR'
        },
        'fields': {
            'timestamp': data['date'],
            'price': price,
            'amount': amount
        }
    }])


def on_trade_message(ws, message):
    logger.setLevel(logging.WARNING)
    data = parse_trade(message)[0]
    if settings.DEBUG:
        logger.debug('parsed: %s', data)

    trader.analyse(data)


def on_error(ws, error):
    if settings.DEBUG:
        logger.exception('Websocket error... %s', error)


def run_ticker(trader):
    logger.setLevel(logging.DEBUG)
    last = 0
    while True:
        print 'asdf'
        response = requests.get(get_ticker_path())
        if response.status_code != 200:
            print('unexpected response: %s%s' % response.status_code, response.content)
            return False

        data = json.loads(response.content)
        if settings.DEBUG:
            logger.debug(data['last'])

        if float(data['last']) != last:
            last = float(data['last'])

            stored = Storage.store([{
                'measurement': 'BTC_EUR',
                'tags': {
                    'asset': 'BTC',
                    'currency': 'EUR'
                },
                'fields': {
                    'timestamp': data['timestamp'],
                    'price': last,
                }
            }])

            # if settings.DEBUG:
            #     logger.debug(stored[0])

            trader.analyse(stored[0])

        sleep(float(settings.BOT_TICKER_INTERVAL))


def run_trader(trader):
    trader = trader  # noqa
    ws_trades = websocket.WebSocketApp(
        get_trades_path(),
        on_message=on_trade_message,
        on_error=on_error
    )
    ws_trades.run_forever()


def run():
    from subprocess import Popen
    from sys import stdout, stdin, stderr
    import time
    import os
    import signal

    commands = [
        './src/manage.py trader',
        './src/manage.py ticker'
    ]

    proc_list = []
    for command in commands:
        print "$ " + command
        proc = Popen(command, shell=True, stdin=stdin, stdout=stdout, stderr=stderr)
        proc_list.append(proc)

    try:
        while True:
            time.sleep(10)
    except KeyboardInterrupt:
        for proc in proc_list:
            os.kill(proc.pid, signal.SIGKILL)
