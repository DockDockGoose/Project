from django.shortcuts import render
from rest_framework import viewsets
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from .serializers import PrevPricesSerializer
from .models import PrevPrices

# ViewSets define the view behavior.
class PrevPricesViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows stocks used on the front end to be viewed or edited.
    """
    queryset = PrevPrices.objects.all()
    serializer_class = PrevPricesSerializer
    filter_backends = [DjangoFilterBackend]

    def post(self, request):
        stockSym = request.data.get("username")
        pri = request.data.get("amount")
        quoteTime = request.data.get("quoteServerTime")

        p = PrevPrices(stockSymbol=stockSym, price=pri, quoteServerTime=quoteTime)
        p.save()
        return Response(status=status.HTTP_200_OK)