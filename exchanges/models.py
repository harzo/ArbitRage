from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator


class Currency(models.Model):
    name = models.CharField(max_length=200)
    code = models.CharField(max_length=10)
    sign = models.CharField(max_length=10)
    sign_after = models.BooleanField(default=True)
    crypto = models.BooleanField(default=False)

    class Meta:
        verbose_name_plural = "currencies"

    def __str__(self):
        return self.name+' ('+self.code+')'


class Exchange(models.Model):
    name = models.CharField(max_length=200)
    display_name = models.CharField(max_length=200)
    url = models.URLField(max_length=200, null=True)
    orderbook_api = models.CharField(max_length=200, null=True)
    ticker_api = models.CharField(max_length=200, null=True)
    maker_fee = models.FloatField(default=0.0, validators=[MinValueValidator(0.0), MaxValueValidator(1.0)])
    taker_fee = models.FloatField(default=0.0, validators=[MinValueValidator(0.0), MaxValueValidator(1.0)])
    active = models.BooleanField(default=True)

    def __str__(self):
        return self.name


class ExchangePair(models.Model):
    exchange = models.ForeignKey(Exchange, on_delete=models.CASCADE, related_name='pairs')
    left = models.ForeignKey(Currency, on_delete=models.CASCADE, related_name='left', null=False)
    right = models.ForeignKey(Currency, on_delete=models.CASCADE, related_name='right', null=False)
    bids = models.TextField(null=True, blank=True)
    asks = models.TextField(null=True, blank=True)
    last_bid = models.FloatField(default=0.0)
    last_ask = models.FloatField(default=0.0)
    active = models.BooleanField(default=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.exchange.name+': '+self.left.code+'/'+self.right.code
