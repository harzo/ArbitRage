from django.db import models
from exchanges.models import Currency


class ExchangePairSettings(models.Model):
    left = models.ForeignKey(Currency, on_delete=models.CASCADE, related_name='sleft', null=False)
    right = models.ForeignKey(Currency, on_delete=models.CASCADE, related_name='sright', null=False)
    update_frequency = models.IntegerField(default=30, null=False)

    class Meta:
        verbose_name_plural = "Exchange Pair Settings"

    def __str__(self):
        return 'Settings: '+self.left.code+'/'+self.right.code
