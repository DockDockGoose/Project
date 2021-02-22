from django.db import models
from django.contrib.auth.models import AbstractUser
from .managers import AccountManager

class Account(AbstractUser):
    username = models.CharField(blank=False, max_length=255, default='', unique=True)
    funds = models.FloatField(default=0.00)
    pendingFunds = models.FloatField(default=0.00)

    objects = AccountManager()

    def __str__(self):
        return self.username