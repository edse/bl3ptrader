from influxdb import InfluxDBClient
from django.conf import settings
import logging


logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
logger.addHandler(ch)


class Storage(object):

    @staticmethod
    def store(data):
        influx_client = Storage.get_client()

        price_len = len(str(data['price_int']))
        price = float(str(data['price_int'])[:price_len - 5] + '.' + str(data['price_int'])[-5:])

        amount_len = len(str(data['amount_int']))
        amount = float(str(data['amount_int'])[:amount_len - 5] + '.' + str(data['amount_int'])[-5:])

        json_body = [{
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
        }]

        influx_client.write_points(json_body)
        return json_body[0]

    @staticmethod
    def get_client():
        return InfluxDBClient(
            settings.INFLUXDB_HOST,
            settings.INFLUXDB_PORT,
            settings.INFLUXDB_USER,
            settings.INFLUXDB_PASS,
            settings.INFLUXDB_DATABASE
        )
