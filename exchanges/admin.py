from django.contrib import admin

from .models import Currency, Exchange, ExchangePair


class ExchangePairInline(admin.TabularInline):
    model = ExchangePair


class CurrencyAdmin(admin.ModelAdmin):
    fields = ['name', 'code', 'sign', 'sign_after', 'crypto']


class ExchangeAdmin(admin.ModelAdmin):
    fields = ['name', 'url', 'orderbook_api', 'ticker_api']
    inlines = [ExchangePairInline]


admin.site.register(Currency, CurrencyAdmin)
admin.site.register(Exchange, ExchangeAdmin)