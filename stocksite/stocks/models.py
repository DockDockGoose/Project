from django.db import models
from djongo import models as djongoModels

class Stock(djongoModels.Model):
    """
    Models a stock in the system.
    """
    stockSymbol = djongoModels.CharField(max_length=50, blank=False)
    price = djongoModels.FloatField(default=0.00)
    quoteServerTime = djongoModels.BigIntegerField(default=0)
    sharesAmount = djongoModels.FloatField(default=0.00)

    objects = djongoModels.DjongoManager()

    class Meta:
        abstract = True

    def __str__(self):
        return self.stockSymbol