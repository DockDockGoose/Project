from django.shortcuts import render
from rest_framework import generics

from .models import Account
from .serializers import AccountSerializer

# TODO: Implement Account view logic
class AccountListView(generics.ListAPIView):
    queryset = Account.objects.all()
    serializer_class = AccountSerializer