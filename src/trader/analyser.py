from django.conf import settings
from .models import Advice
from .storage import Storage
from django.utils import timezone
import datetime
import logging


logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
logger.addHandler(ch)


class Analyser(object):
    @staticmethod
    def recentAdvice(pair, position):
        date = timezone.now() - datetime.timedelta(
            seconds=settings.BOT_ADVICE_TTL)

        return Advice.objects.filter(
            pair=pair,
            time__gte=date,
            position=position
        )

    @staticmethod
    def bestAdvice(position):
        date = timezone.now() - datetime.timedelta(seconds=settings.BOT_ADVICE_TTL)
        order = '-diff' if position == 'long' else 'diff'
        return Advice.objects.filter(time__gte=date, position=position).order_by(order).all().first()

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

        q = """SELECT last(price) as price,
            moving_average(mean(price), 20) as ma20,
            moving_average(mean(price), 10) as ma10
            FROM "{}"
            WHERE time > now() - 6h
            GROUP BY time(5m) fill(none) ORDER BY DESC
            """.format(pair)

        rs = influx_client.query(q)
        result = list(rs.get_points(measurement=pair))

        for r in result:
            if r['price']:
                current['price'] = r['price']
                current['time'] = r['time']
            if r['ma10']:
                current['ma10'] = r['ma10']
            if r['ma20']:
                current['ma20'] = r['ma20']
            if current['time'] and current['price'] and current['ma10'] and current['ma20']:
                break

        if current['time'] and current['price'] and current['ma10'] and current['ma20']:
            # diff
            diff = current['ma20'] - current['ma10']

            logger.debug('{} DIFF: {}'.format(pair, diff))

            if diff <= -0.00025:
                # short
                logger.debug('SHORT')
                # position = 'short'
                # tweet = '{title}\n{position}\n{price}\n{diff}'.format(
                #     title=settings.TWEET_TITLE.format(pair),
                #     position=settings.TWEET_POSITION.format(position),
                #     price=settings.TWEET_PRICE.format(current['price']),
                #     diff=diff
                # )
            elif diff >= 0.00025:
                # short
                logger.debug('LONG')
                # position = 'long'
                # tweet = '{title}\n{position}\n{price}\n{diff}'.format(
                #     title=settings.TWEET_TITLE.format(pair),
                #     position=settings.TWEET_POSITION.format(position),
                #     price=settings.TWEET_PRICE.format(current['price']),
                #     diff=diff
                # )

            # if tweet:
            #     if Analizer.recentAdvice(pair=pair, position=position):
            #         logger.info('{} {} - Advice already published!'.format(pair, position))
            #         return None

            #     if settings.BOT_TWEET:
            #         tweet(tweet)

            #     Advice.objects.create(**{
            #         'pair': data['measurement'],
            #         'position': position,
            #         'price': current['price'],
            #         'diff': diff,
            #         'tweet': tweet,
            #     })

            #     logger.info(tweet)

            #     best_short = Analizer.bestAdvice('short')
            #     if best_short:
            #         logger.info('Best short: {}'.format(best_short.tweet))

            #     best_long = Analizer.bestAdvice('long')
            #     if best_long:
            #         logger.info('Best long: {}'.format(best_long.tweet))
