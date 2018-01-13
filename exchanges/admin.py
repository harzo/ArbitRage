from django.contrib import admin

from .models import Currency, Exchange, ExchangePair


class ExchangePairInline(admin.TabularInline):
    model = ExchangePair


class CurrencyAdmin(admin.ModelAdmin):
    fields = ['name', 'code', 'sign', 'sign_after', 'crypto']


class ExchangeAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'url', 'active')
    list_editable = ('active',)

    fields = ['name', 'display_name', 'url', 'orderbook_api', 'ticker_api', 'maker_fee', 'taker_fee', 'active']
    inlines = [ExchangePairInline]


admin.site.register(Currency, CurrencyAdmin)
admin.site.register(Exchange, ExchangeAdmin)