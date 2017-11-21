# TWITTER
TWITTER_CONSUMER_KEY = 'CHANGE-ME'
TWITTER_CONSUMER_SECRET = 'CHANGE-ME'
TWITTER_ACCESS_TOKEN = 'CHANGE-ME'
TWITTER_ACCESS_TOKEN_SECRET = 'CHANGE-ME'

# TWEET
TWEET_TITLE = '#BL3P #{} Trading advice!'
TWEET_POSITION = 'Position to take: {}'
TWEET_PRICE = 'Market price: {}'
TWEET_TIME = 'Based on market time: {}'

# INFLUXDB
INFLUXDB_HOST = 'localhost'
INFLUXDB_PORT = 8086
INFLUXDB_USER = 'root'
INFLUXDB_PASS = 'root'
INFLUXDB_DATABASE = 'bl3ptrader'

# BOT
BOT_TWEET = True
BOT_MIN_DIFF = -0.00025
BOT_MAX_DIFF = 0.00025
BOT_ADVICE_TTL = 5 * 60
BOT_DATA_SAMPLE_RANGE = '3h'
BOT_DATA_SAMPLE_GROUP = '1m'
BOT_DATA_SAMPLE_MA1 = '10'
BOT_DATA_SAMPLE_MA2 = '20'

EXCHANGES = {
    'BL3P': {
        'name': 'BL3P',
        'public': {
            'url': 'wss://api.bl3p.eu/1/BTCEUR/trades',
        },
        'private': {
            'url': 'https://api.bl3p.eu/1/',
            'public_key': 'CHANGE-ME',
            'private_key': 'CHANGE-ME',
            'paths': {
                'get_balance': 'GENMKT/money/info',
                'add_order': 'BTCEUR/money/order/add'
            }
        },
        'trade_fee': 0.255,
        'compensate_fee': True,     # s
        'intercalate_trade': True,  # intercalte buy and sell orders
        'safe_trade': True,         # dont sell cheap, dont buy high
        'min_buy_value': 1000000,   # 10 EUR    (*1e5)
        'min_sell_value': 50000,    # 0.0005 BTC  (*1e8)
        'soft_run': False
    }
}
