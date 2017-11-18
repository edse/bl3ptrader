import logging
from .constants import *  # noqa

logger = logging.getLogger('bl3ptrader')
logger.setLevel(logging.DEBUG)
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
logger.addHandler(ch)
