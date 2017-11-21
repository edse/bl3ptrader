from django.conf import settings
from .storage import Storage
from .trader import Trader
from .base import *  # noqa


class Analyser(object):
    @staticmethod
    def checkTrend():
        """
        Check the last 2 records from the last 30m grouped by 1m
        Returns:
            int(-10): when the trending is down and a sell action is required
            int(-1): when the trending is down
            int(0): when in no trend or no enough data
            int(1): when the trending is up
            int(10): when the trending is up and a sell action is required
        """
        trend = 0
        influx_client = Storage.get_client()

        q = """SELECT mean("diff") as diff
            FROM "MA1_MA2_DIFF"
            WHERE time > now() - 30m
            GROUP BY time(1m) fill(previous)"""
        rs = influx_client.query(q)

        if len(list(rs.get_points(measurement='MA1_MA2_DIFF'))) < 2:
            return 0  # no enough data

        d1 = list(rs.get_points(measurement='MA1_MA2_DIFF'))[-2]
        d2 = list(rs.get_points(measurement='MA1_MA2_DIFF'))[-1]

        if 'diff' in d1 and 'diff' in d2:
            d1 = d1['diff']
            d2 = d2['diff']

            if d2 > d1:
                # growing
                if d1 <= 0 and d2 > 0:
                    trend = 10  # buy action
                else:
                    trend = 1
            elif d2 < d1:
                # shrinking
                if d2 <= 0 and d1 > 0:
                    trend = -10  # sell action
                else:
                    trend = -1

        Storage.store([{
            'measurement': 'TREND',
            'fields': {
                'trend': trend
            }
        }])

        return trend

    @staticmethod
    def analyse(data):
        # logger.debug('Analysing...')
        range = settings.BOT_DATA_SAMPLE_RANGE  # 3h
        group = settings.BOT_DATA_SAMPLE_GROUP  # 1m
        ma1 = settings.BOT_DATA_SAMPLE_MA1      # 10
        ma2 = settings.BOT_DATA_SAMPLE_MA2      # 20

        influx_client = Storage.get_client()
        pair = data['measurement']
        # tweet = None
        # position = ''
        current = {
            'time': None,
            'price': None,
            'ma1': None,
            'ma2': None,
        }

        #
        # TODO: Replace 3 queries by 1
        #
        q = """SELECT mean("price") as price
            FROM "BTC_EUR"
            WHERE time > now() - {range}
            GROUP BY time({group}) fill(previous)""".format(
            range=range,
            group=group
        )
        rs = influx_client.query(q)
        r = list(rs.get_points(measurement=pair))[-1]
        if 'price' in r:
            current['price'] = r['price']
            current['time'] = r['time']

        q = """SELECT moving_average(mean("price"), {ma1}) as ma1
            FROM "BTC_EUR"
            WHERE time > now() - {range}
            GROUP BY time({group}) fill(linear)""".format(
            ma1=ma1,
            range=range,
            group=group
        )
        rs = influx_client.query(q)
        r = list(rs.get_points(measurement=pair))[-1]
        current['ma1'] = r['ma1']
        if 'ma1' in r:
            current['ma1'] = r['ma1']

        q = """SELECT moving_average(mean("price"), {ma2}) as ma2
            FROM "BTC_EUR"
            WHERE time > now() - {range}
            GROUP BY time({group}) fill(linear)""".format(
            ma2=ma2,
            range=range,
            group=group
        )
        rs = influx_client.query(q)
        r = list(rs.get_points(measurement=pair))[-1]
        current['ma2'] = r['ma2']
        if 'ma2' in r:
            current['ma2'] = r['ma2']

        # logger.info('Current: %s', current)

        if current['time'] and current['price'] and current['ma1'] and current['ma2']:
            # diff
            diff = current['ma1'] - current['ma2']
            # logger.info('%s MAs diff: %s', pair, diff)

            Storage.store([{
                'measurement': 'MA1_MA2_DIFF',
                'tags': {
                    'asset': 'MA1',
                    'currency': 'MA2'
                },
                'fields': {
                    'timestamp': current['time'],
                    'diff': diff,
                    'ma1': current['ma1'],
                    'ma2': current['ma2'],
                }
            }])

        trend = Analyser.checkTrend()

        trader = Trader()
        trader.take_action(trend=trend, current=current)
