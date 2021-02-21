from django.shortcuts import render
from rest_framework import viewsets
from .models import Stock
from .serializers import StockSerializer

# TODO: Implement Stock view logic
class StockViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows stocks to be viewed or edited.
    """
    queryset = Stock.objects.all()
    serializer_class = StockSerializer