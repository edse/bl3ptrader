from django.core.management.base import BaseCommand
from trader import watcher
import logging


logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
logger.addHandler(ch)


class Command(BaseCommand):
    help = 'Turn the bot ON and... To the moon!'

    def handle(self, *args, **options):
        watcher.run()
