from django.db import models
from djongo import models as djongoModels

class Trigger(djongoModels.Model):
    """
    Models a trigger in the system.
    """
    id = djongoModels.CharField(max_length=50, primary_key=True)
    username = djongoModels.CharField(max_length=50, blank=False)
    type = djongoModels.CharField(max_length=50, blank=False)
    stockSymbol = djongoModels.CharField(max_length=50, blank=False)
    price = djongoModels.FloatField(default=0.00)
    sharesAmount = djongoModels.FloatField(default=0.00)

    def __str__(self):
        return '%s %s %s' % (self.username, self.type, self.stockSymbol)