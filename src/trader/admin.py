from django.contrib import admin
from .models import Advice, Trade


@admin.register(Advice)
class AdviceAdmin(admin.ModelAdmin):
    list_display = ('pair', 'position', 'price', 'diff', 'updated_at')
    list_filter = ('pair', 'position')
    fields = ('pair', 'position', 'price', 'diff', 'tweet')


@admin.register(Trade)
class TradeAdmin(admin.ModelAdmin):
    pass
