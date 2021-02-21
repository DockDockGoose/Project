from django.db import models
from django.contrib.auth.models import AbstractUser

class Account(AbstractUser):
    userId = models.CharField(blank=True, max_length=255)
    funds = models.FloatField(default=0.00)
    pendingFunds = models.FloatField(default=0.00)

    def __str__(self):
        return self.userId