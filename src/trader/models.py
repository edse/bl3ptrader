from django.db import models


class Advice(models.Model):
    pair = models.CharField(max_length=30)
    position = models.CharField(max_length=30)
    diff = models.FloatField(default=0)
    price = models.FloatField()
    tweet = models.CharField(max_length=140)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class Trade(models.Model):
    amount = models.FloatField()
    price = models.FloatField()
    total = models.FloatField()
    tweet = models.CharField(max_length=140)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
