from django.shortcuts import render
from rest_framework import viewsets
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from .serializers import FrontEndStockSerializer
from .models import FrontEndStock

# ViewSets define the view behavior.
class FrontStocksViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows stocks used on the front end to be viewed or edited.
    """
    queryset = FrontEndStock.objects.all()
    serializer_class = FrontEndStockSerializer
    filter_backends = [DjangoFilterBackend]

    def post(self, request):
        stockSym = request.data.get("username")
        pri = request.data.get("amount")
        quoteTime = request.data.get("quoteServerTime")

        f = FrontEndStock(stockSymbol=stockSym, price=pri, quoteServerTime=quoteTime)
        f.save()
        return Response(status=status.HTTP_200_OK)