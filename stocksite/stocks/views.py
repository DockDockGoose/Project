from django.shortcuts import render
from django.db.models import F
from rest_framework import viewsets
from .models import Stock
from .serializers import StockSerializer
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .mockQuoteServer import MockQuoteServer
from accounts.models import Account
from transactions.models import Transaction
from time import time

# TODO: Implement Stock view logic
class StockViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows stocks to be viewed or edited.
    """
    queryset = Stock.objects.all()
    serializer_class = StockSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['stockSymbol']
    ordering = ['quoteServerTime']


# class QuoteView(APIView):
#     """
#     API endpoint that allows a stock to be quoted.
#     """
#     def get(self, request):
#         stockSymbol = request.data.get('stockSymbol')

#         MockQuoteServer.getQuote()
#         # Query the QuoteServer


class BuyView(APIView):
    """
    API endpoint that allows stocks to be bought.
    """
    def post(self, request):
         # Get request data
        username = request.data.get("username")
        stockSymbol = request.data.get("stockSymbol")
        amount = float(request.data.get("amount"))
        
        # Log buy request transaction
        transaction = Transaction(
                type='userCommand',
                timestamp=int(time()*1000),
                server='DOCK1',
                transactionNum = Transaction.objects.last().transactionNum + 1,
                command='BUY',
                username=username,
                stockSymbol=stockSymbol,
                amount=amount,
            )
        transaction.save()

        # Find user account
        account = Account.objects.filter(username=username).first()

        # Check funds permit action, log error event to transaction if not
        if account.funds < amount:
            return Response("Insufficient funds :(.", status=status.HTTP_412_PRECONDITION_FAILED)

        return Response(status=status.HTTP_200_OK)
