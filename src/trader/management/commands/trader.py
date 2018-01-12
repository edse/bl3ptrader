from django.core.management.base import BaseCommand
from trader import trader


class Command(BaseCommand):

    def handle(self, *args, **options):
        trader = Trader()
        trader.start_trader()
