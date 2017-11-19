from django.db import models


class Advice(models.Model):
    pair = models.CharField(max_length=30)
    position = models.CharField(max_length=30)
    diff = models.FloatField(default=0)
    price = models.FloatField()
    tweet = models.CharField(max_length=280)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class Trade(models.Model):
    BUY = 'BUY'
    SELL = 'SELL'
    TRADE_TYPES = (
        (BUY, 'Buy'),
        (SELL, 'Sell'),
    )

    amount = models.FloatField()
    price = models.FloatField()
    total = models.FloatField()
    fee = models.FloatField()
    type = models.CharField(choices=TRADE_TYPES, max_length=25)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return '#{} - {}: {} ({})'.format(
            self.id, self.type, self.amount, self.price
        )
