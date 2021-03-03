from django.db import models
from djongo import models as djongoModels

class FrontEndStock(djongoModels.Model):
    """
    Models a stock for the front end in the system.
    """
    stockSymbol = djongoModels.CharField(max_length=50, blank=False)
    price = djongoModels.FloatField(default=0.00)
    quoteServerTime = djongoModels.BigIntegerField(default=0)
    #sharesAmount = djongoModels.FloatField(default=0.00)

    def __str__(self):
        return self.stockSymbol