from django.db import models


class Currency(models.Model):
    name = models.CharField(max_length=200)
    code = models.CharField(max_length=10)
    sign = models.CharField(max_length=10)
    sign_after = models.BooleanField(default=True)
    crypto = models.BooleanField(default=False)

    def __str__(self):
        return self.name+' ('+self.code+')'


class Exchange(models.Model):
    name = models.CharField(max_length=200)

    def __str__(self):
        return self.name


class ExchangePair(models.Model):
    exchange = models.ForeignKey(Exchange, on_delete=models.CASCADE, related_name='pairs')
    left = models.ForeignKey(Currency, on_delete=models.CASCADE, related_name='left', null=False)
    right = models.ForeignKey(Currency, on_delete=models.CASCADE, related_name='right', null=False)

    def __str__(self):
        return self.exchange.name+': '+self.left.code+'/'+self.right.code
