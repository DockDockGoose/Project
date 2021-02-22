from django.db import models
from django import forms
from djongo import models as djongoModels

class Stock(djongoModels.Model):
    """
    Models a stock in the system.
    """
    stockSymbol = djongoModels.CharField(max_length=50, blank=False)
    price = djongoModels.FloatField(default=0.00)
    quoteServerTime = djongoModels.BigIntegerField(default=0)

    objects = djongoModels.DjongoManager()

    class Meta: 
        abstract = True

    def __str__(self): 
        return self.stockSymbol
        

class Shares(djongoModels.Model):
    """
    Models a stockShare in the system.
    """
    stocks = djongoModels.EmbeddedField(
        model_container=Stock
    )

    sharesAmount = djongoModels.FloatField(default=0.00)

    objects = djongoModels.DjongoManager()

    class Meta:
        abstract = True

    def __str__(self):
        return self.sharesAmount