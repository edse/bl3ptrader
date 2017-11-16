from django.conf import settings
from .storage import Storage
from .analyser import Analyser
import logging
import websocket
import json


logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
logger.addHandler(ch)
ws = None


def on_message(ws, data):
    logger.debug('Message received: %s', data)
    payload = Storage.store(json.loads(data))
    Analyser.analyse(payload)


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
