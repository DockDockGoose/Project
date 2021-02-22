from django.db import models
from django.contrib.auth.models import AbstractUser
from .managers import AccountManager
from djongo import models as djongoModels
from stocks.models import Shares


class Account(AbstractUser):
    username = models.CharField(blank=False, max_length=255, unique=True)
    funds = models.FloatField(default=0.00)
    pendingFunds = models.FloatField(default=0.00)
    shares = djongoModels.ArrayField(
        model_container=Shares
    )

    objects = AccountManager()

    def __str__(self):
        return self.username 