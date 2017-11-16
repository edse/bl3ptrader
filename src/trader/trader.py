from datetime import datetime
from time import mktime
import hmac
import json
import urllib
import base64
import hashlib
import requests
from django.conf import settings


class Trader(object):
    buy_margin = 2   # percentage
    sell_margin = 2  # percentage

    def get_nonce(self):
        dt = datetime.utcnow()
        return str(mktime(dt.timetuple()) * 1000 * 1000 + dt.microsecond)

    def get_signature(self, body):
        return base64.b64encode(
            hmac.new(
                base64.b64decode(settings.EXCHANGES['BL3P']['private']['private_key']),
                body,
                hashlib.sha512
            ).digest()
        )

    def execute(self, path, data, headers):
        response = requests.post(path, params=data, headers=headers)
        if response.status_code != 200:
            raise Exception('unexpected response: %s%s' % response.status_code, response.content)

        return json.loads(response.content)

    def call(self, path, params):
        # generate the POST data
        params['nonce'] = self.get_nonce()
        post_data = urllib.urlencode(params)
        body = '%s%c%s' % (path, 0x00, urllib.urlencode(params))
        fullpath = settings.EXCHANGES['BL3P']['private']['url'] + path

        # set headers
        headers = {
            'Rest-Key': settings.EXCHANGES['BL3P']['private']['public_key'],
            'Rest-Sign': self.get_signature(body),
        }

        # execute call
        return self.execute(
            path=fullpath,
            data=post_data,
            headers=headers
        )
