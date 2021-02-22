from django.db import models

class Stock(models.Model):
    """
    Models a stock in the system.
    """
    stockSymbol = models.CharField(max_length=50, blank=False)
    price = models.FloatField(default=0.00)
    quoteServerTime = models.BigIntegerField(default=0)

    def __str__(self):
        return self.stockSymbol