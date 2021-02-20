from django.db import models

class Transaction(models.Model):
    """
    Models each transaction on the system.
    """
    type = models.CharField(max_length=50, blank=True)
    # UserCommand
    timestamp = models.BigIntegerField(default=0)
    server = models.CharField(max_length=50, blank=True)
    transactionNum = models.IntegerField(blank=True)
    command = models.CharField(max_length=50, blank=True)
    username = models.CharField(max_length=50, blank=True)
    stockSymbol = models.CharField(max_length=50, blank=True)
    fileName = models.CharField(max_length=50, blank=True)
    # Account Transaction
    action = models.CharField(max_length=50, blank=True)
    # Funds
    amount = models.FloatField(blank=True)
    # Quoteserver
    price = models.FloatField(blank=True)
    quoteServerTime = models.BigIntegerField(default=0)
    cryptoKey = models.CharField(max_length=50, blank=True)
    # Logs
    systemEvent = models.CharField(max_length=50, blank=True)
    errorEvent = models.CharField(max_length=50, blank=True)
    errorMessage = models.CharField(max_length=50, blank=True)
    debugEvent = models.CharField(max_length=50, blank=True)
    debugMessage = models.CharField(max_length=50, blank=True)

    # Used for testing
    def __str__(self):
        return self.command