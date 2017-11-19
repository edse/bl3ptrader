from django.conf import settings
from .storage import Storage
from .trader import Trader
from .models import Trade
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
        influx_client = Storage.get_client()
        q = """SELECT mean("diff") as diff
            FROM "MA10_MA20_DIFF"
            WHERE time > now() - 30m
            GROUP BY time(1m) fill(previous)"""
        rs = influx_client.query(q)

        d1 = list(rs.get_points(measurement='MA10_MA20_DIFF'))[-2]
        d2 = list(rs.get_points(measurement='MA10_MA20_DIFF'))[-1]

        if 'diff' in d1 and 'diff' in d2:
            d1 = d1['diff']
            d2 = d2['diff']

            if d2 > d1:
                # diff growing
                if d1 <= 0 and d2 > 0:
                    # buy action
                    return 10
                return 1
            elif d2 < d1:
                # diff shrinking
                if d2 <= 0 and d1 > 0:
                    # sell action
                    return -10
                return -1
            else:
                # no trend
                return 0
        else:
            # no enough data
            return 0

    @staticmethod
    def analyse(data):
        logger.debug('Analysing...')
        influx_client = Storage.get_client()
        pair = data['measurement']
        # tweet = None
        # position = ''
        current = {
            'time': None,
            'price': None,
            'ma10': None,
            'ma20': None,
        }

        q = """SELECT mean("price") as price
            FROM "BTC_EUR"
            WHERE time > now() - 3h
            GROUP BY time(1m) fill(previous)"""
        rs = influx_client.query(q)
        r = list(rs.get_points(measurement=pair))[-1]
        if 'price' in r:
            current['price'] = r['price']
            current['time'] = r['time']

        q = """SELECT moving_average(mean("price"), 10) as ma10
            FROM "BTC_EUR"
            WHERE time > now() - 3h
            GROUP BY time(1m) fill(previous)"""
        rs = influx_client.query(q)
        r = list(rs.get_points(measurement=pair))[-1]
        current['ma10'] = r['ma10']
        if 'ma10' in r:
            current['ma10'] = r['ma10']

        q = """SELECT moving_average(mean("price"), 20) as ma20
            FROM "BTC_EUR"
            WHERE time > now() - 3h
            GROUP BY time(1m) fill(previous)"""
        rs = influx_client.query(q)
        r = list(rs.get_points(measurement=pair))[-1]
        current['ma20'] = r['ma20']
        if 'ma20' in r:
            current['ma20'] = r['ma20']

        #
        # TODO: RUNING THE ABOVE QUERIES AS ONE
        #

        logger.info('Current: %s', current)

        if current['time'] and current['price'] and current['ma10'] and current['ma20']:
            # diff
            diff = current['ma10'] - current['ma20']
            logger.info('%s MAs diff: %s', pair, diff)

            Storage.store([{
                'measurement': 'MA10_MA20_DIFF',
                'tags': {
                    'asset': 'MA10',
                    'currency': 'MA20'
                },
                'fields': {
                    'timestamp': current['time'],
                    'diff': diff,
                    'ma10': current['ma10'],
                    'ma20': current['ma20'],
                }
            }])

        trader = Trader()
        trend = Analyser.checkTrend()

        Storage.store([{
            'measurement': 'TREND',
            'fields': {
                'trend': trend
            }
        }])

        last_order = Trade.objects.all().last()

        # BUY
        if trend == 10:
            if last_order:
                if settings.EXCHANGES['BL3P']['intercalate_trade']:
                    # last order must be a sell
                    if last_order.type == Trade.BUY:
                        logger.exception('Trying to buy after a buy with intercalate_trade set to true!')
                        return False

                if settings.EXCHANGES['BL3P']['safe_trade']:
                    # check if the buy price is cheaper than the last sell
                    if current['price'] >= last_order.price:
                        logger.exception('Trying to buy for a higher price than last sell with safe_trade set to true!')
                        return False

            trader.buy(current['price'], settings.EXCHANGES['BL3P']['soft_run'])

        # SELL
        elif trend == -10:
            if last_order:
                if settings.EXCHANGES['BL3P']['intercalate_trade']:
                    # last order must be a buy
                    if last_order.type == Trade.SELL:
                        logger.exception('Trying to sell after a sell with intercalate_trade set to true!')
                        return False

                if settings.EXCHANGES['BL3P']['safe_trade']:
                    # check if the sell price is higher than the last buy
                    if current['price'] <= last_order.price:
                        logger.exception('Trying to sell for a cheaper price than last buy with safe_trade set to true!')
                        return False

            trader.sell(current['price'], settings.EXCHANGES['BL3P']['soft_run'])
