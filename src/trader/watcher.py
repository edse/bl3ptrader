from django.conf import settings
from .storage import Storage
from .analyser import Analyser
import json
import websocket
from .base import *  # noqa

ws = None


def on_message(ws, data):
    # logger.debug('Message received: %s', data)

    # parse data
    data = json.loads(data)
    price_len = len(str(data['price_int']))
    price = float(str(data['price_int'])[:price_len - 5] + '.' + str(data['price_int'])[-5:])
    amount_len = len(str(data['amount_int']))
    amount = float(str(data['amount_int'])[:amount_len - 5] + '.' + str(data['amount_int'])[-5:])

    payload = Storage.store([{
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

    Analyser.analyse(payload[0])


def on_error(ws, error):
    logger.exception('Websocket error... %s', error)


def run():
    websocket.enableTrace(True)
    ws = websocket.WebSocketApp(
        settings.EXCHANGES['BL3P']['public']['url'],
        on_message=on_message,
        on_error=on_error,
    )
    ws.run_forever()
