# EXCHANGES
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
        },
        'trade_fee': 0.25,
        'intercalate_trade': True,  # intercalte buy and sell orders
        'safe_trade': True,         # dont sell cheap, dont buy high
        'min_buy_value': 1000000,   # 10 EUR    (*1e5)
        'min_sell_value': 5000000,  # 0.05 BTC  (*1e8)
        'soft_run': True
    }
}

# TWITTER
TWITTER_CONSUMER_KEY = 'CHANGE-ME'
TWITTER_CONSUMER_SECRET = 'CHANGE-ME'
TWITTER_ACCESS_TOKEN = 'CHANGE-ME'
TWITTER_ACCESS_TOKEN_SECRET = 'CHANGE-ME'
