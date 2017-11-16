from influxdb import InfluxDBClient
from django.conf import settings
from .base import *  # noqa


class Storage(object):

    @staticmethod
    def store(data):
        influx_client = Storage.get_client()
        influx_client.write_points(data)
        return data

    @staticmethod
    def get_client():
        return InfluxDBClient(
            settings.INFLUXDB_HOST,
            settings.INFLUXDB_PORT,
            settings.INFLUXDB_USER,
            settings.INFLUXDB_PASS,
            settings.INFLUXDB_DATABASE
        )
