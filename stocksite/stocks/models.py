from django.db import models

class Stock(models.Model):
    """
    Models a stock in the system.
    """
    stockSymbol = models.CharField(max_length=50, blank=False, default='')
    price = models.FloatField(default=0.00)

    def __str__(self):
        return self.stockSymbol