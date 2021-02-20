from django.db import models

class Transactions(models.Model):
    type = models.CharField(max_length=50, blank=True)
    userId = models.CharField(max_length=50, blank=True)
    stockSymbol = models.CharField(max_length=50, blank=True)
    userCommand = models.CharField(max_length=50, blank=True)
    timestamp = models.BigIntegerField(default=0)
    cryptoKey = models.CharField(max_length=50, blank=True)
    price = models.FloatField(blank=True)
    server = models.CharField(max_length=50, blank=True)
    transactionNum = models.IntegerField(blank=True)
    amount = models.FloatField(blank=True)
    fileName = models.CharField(max_length=50, blank=True)