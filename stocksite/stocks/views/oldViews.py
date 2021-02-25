# from django.db.models import F
# from rest_framework import viewsets
# from .serializers import StockSerializer
from django.shortcuts import render
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.views import APIView
from rest_framework.generics import ListAPIView
from rest_framework.response import Response
from rest_framework import status
from .models import Stock
from accounts.models import Account
from stocks.models import Stock
from transactions.models import Transaction
from .mockQuoteServer import MockQuoteServer
from time import time

# class StockViewSet(viewsets.ModelViewSet):
#     queryset = Stock.objects.all()
#     serializer_class = StockSerializer

# class SharesViewSet(viewsets.ModelViewSet):
#     queryset = Shares.objects.all()
#     serializer_class = SceneSerializer


class QuoteView(APIView):
    """
    API endpoint that allows a stock to be quoted.
    """
    def get(self, request):
        stockSymbol = request.data.get('stockSymbol')
        username = request.data.get('username')

        # Log the quote command transaction
        transaction = Transaction(
                type='userCommand',
                timestamp=int(time()*1000),
                server='DOCK1',
                transactionNum = Transaction.objects.last().transactionNum + 1,
                command='QUOTE',
                username=username,
                stockSymbol=stockSymbol,
            )
        transaction.save()

        # Query the QuoteServer (Try/Catch for systemEvent/errorEvent logging)
        quoteQuery = MockQuoteServer.getQuote(username, stockSymbol)
        # TODO: Cache the recently quoted stock price

        #  Log quoteServer transaction (only increment transactionNum for userCommands?)
        transaction = Transaction(
                type='quoteServer',
                timestamp=int(time()*1000),
                server='DOCK1',
                transactionNum = Transaction.objects.last().transactionNum,
                price=quoteQuery['price'],
                username=username,
                stockSymbol=stockSymbol,
                quoteServerTime=quoteQuery['quoteServerTime'],
                cryptoKey=quoteQuery['cryptoKey']
            )
        transaction.save()

        return Response(quoteQuery, status=status.HTTP_200_OK)


class BuyView(APIView):
    """
    API endpoint that allows stocks to be bought.
    """
    def post(self, request):
        # Get request data
        username = request.data.get("username")
        stockSymbol = request.data.get("stockSymbol")
        amount = float(request.data.get("amount"))

        # Find user account
        account = Account.objects.filter(username=username).first()

        # If account is non-existing, log errorEvent to Transaction
        if account is None:
            transaction = Transaction(
                type='errorEvent',
                timestamp=int(time()*1000),
                server='DOCK1',
                transactionNum = Transaction.objects.last().transactionNum,
                command='BUY',
                username=username,
                stockSymbol=stockSymbol,
                amount=amount,
                errorMessage='Account does not exist.',
            )
            transaction.save()
            return Response("Account doesn't exist.", status=status.HTTP_412_PRECONDITION_FAILED)

        # Check if funds permit action, log error event to transaction if not
        if account.funds < amount:
            transaction = Transaction(
                type='errorEvent',
                timestamp=int(time()*1000),
                server='DOCK1',
                transactionNum = Transaction.objects.last().transactionNum,
                command='BUY',
                username=username,
                stockSymbol=stockSymbol,
                amount=amount,
                errorMessage='Insufficient funds :(.',
            )
            transaction.save()
            return Response("Insufficient funds :(.", status=status.HTTP_412_PRECONDITION_FAILED)

        # Log buy transaction
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

        return Response(status=status.HTTP_200_OK)


class SellView(APIView):
    """
    API endpoint that allows stocks to be sold.
    """
    def post(self, request):
        # Get request data
        username = request.data.get("username")
        stockSymbol = request.data.get("stockSymbol")
        amount = float(request.data.get("amount"))

        # Find user account
        account = Account.objects.filter(username=username).first()

        # If account is non-existing, log errorEvent to Transaction
        if account is None:
            transaction = Transaction(
                type='errorEvent',
                timestamp=int(time()*1000),
                server='DOCK1',
                transactionNum = Transaction.objects.last().transactionNum,
                command='SELL',
                username=username,
                stockSymbol=stockSymbol,
                amount=amount,
                errorMessage='Account does not exist.',
            )
            transaction.save()
            return Response("Account doesn't exist.", status=status.HTTP_412_PRECONDITION_FAILED)

        # Search Account for stock, log error event to transaction if doesnt exist
        stock = getByStockSymbol(account.stocks, stockSymbol)
        if stock is None:
            transaction = Transaction(
                type='errorEvent',
                timestamp=int(time()*1000),
                server='DOCK1',
                transactionNum = Transaction.objects.last().transactionNum,
                command='BUY',
                username=username,
                stockSymbol=stockSymbol,
                amount=amount,
                errorMessage='Stock not owned.',
            )
            transaction.save()
            return Response("Stock not owned.", status=status.HTTP_412_PRECONDITION_FAILED)

        # Check if shares amount permit action, og error event to transaction if not 
        sharesAmount = stock['sharesAmount']
        if sharesAmount < amount:
            transaction = Transaction(
                type='errorEvent',
                timestamp=int(time()*1000),
                server='DOCK1',
                transactionNum = Transaction.objects.last().transactionNum,
                command='SELL',
                username=username,
                stockSymbol=stockSymbol,
                amount=amount,
                errorMessage='Not enough shares to sell.',
            )
            transaction.save()
            return Response("Not enough shares to sell.", status=status.HTTP_412_PRECONDITION_FAILED)

        # Log sell transaction
        transaction = Transaction(
                type='userCommand',
                timestamp=int(time()*1000),
                server='DOCK1',
                transactionNum = Transaction.objects.last().transactionNum + 1,
                command='SELL',
                username=username,
                stockSymbol=stockSymbol,
                amount=amount,
            )
        transaction.save()

        return Response(status=status.HTTP_200_OK)


class CommitBuyView(APIView):
    """
    API endpoint for confirming the buy of a stock.
    """
    def post(self, request):
        # Get request data
        username = request.data.get("username")
        # Test values (uncomment to populate the db)
        # stockSymbol = 'NISSAN'
        # amount = 500.00
        
        # Check cache for recent buy transaction (within 60 sec), if non-existent log errorEvent
        # stockSymbol = fromcache
        # amount = fromcache

        # Find user account
        account = Account.objects.filter(username=username).first()
        
        # TODO: Check for quote in cache (if not in cache/is stale perform query)
        # Query the QuoteServer (Try/Catch for systemEvent/errorEvent logging)
        quoteQuery = MockQuoteServer.getQuote(username, stockSymbol)

        # Remove amount from account funds
        account.funds -= amount

        # Search account for stock
        stock = getByStockSymbol(account.stocks, stockSymbol)

        # Create new stock in account if non-existing
        if stock is None:
            newStock = {'stockSymbol':stockSymbol, 'price':quoteQuery['price'], 'quoteServerTime':quoteQuery['quoteServerTime'], 'sharesAmount':amount/quoteQuery['price']}
            account.stocks.append(newStock)
        else:
            # If stock exists in account, add amount/price to stock sharesAmount
            stock['sharesAmount'] += amount/quoteQuery['price']

        account.save()

        # Log commit buy transaction
        transaction = Transaction(
                type='userCommand',
                timestamp=int(time()*1000),
                server='DOCK1',
                transactionNum = Transaction.objects.last().transactionNum + 1,
                command='COMMIT_BUY',
                username=username,
                stockSymbol=stockSymbol,
                amount=amount,
            )
        transaction.save()

        return Response(status=status.HTTP_200_OK)


class CommitSellView(APIView):
    """
    API endpoint for confirming the sell of a stock.
    """
    def post(self, request):
        # Get request data
        username = request.data.get("username")
        # Test values (uncomment to populate the db)
        # stockSymbol = 'NISSAN'
        # amount = 300.00
        
        # Check cache for recent sell transaction (within 60 sec), if non-existent log errorEvent
        # stockSymbol = fromcache
        # amount = fromcache

        # Find user account
        account = Account.objects.filter(username=username).first()

        # Search account for stock
        stock = getByStockSymbol(account.stocks, stockSymbol)

        # Subtract amount from stock sharesAmount & add amount to account funds
        stock['sharesAmount'] -= amount
        account.funds += amount
        account.save()

        # Log commit sell transaction
        transaction = Transaction(
                type='userCommand',
                timestamp=int(time()*1000),
                server='DOCK1',
                transactionNum = Transaction.objects.last().transactionNum + 1,
                command='COMMIT_SELL',
                username=username,
                stockSymbol=stockSymbol,
                amount=amount,
            )
        transaction.save()

        return Response(status=status.HTTP_200_OK)


def getByStockSymbol(stocks, stockSymbol): 
    """
    Searches for the dictionary containing the correct stockSymbol in the list.
    """
    return next((item for item in stocks if item['stockSymbol'] == stockSymbol), None)
