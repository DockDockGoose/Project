from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from accounts.models import Account
from transactions.models import Transaction
from time import time


class SellView(APIView):
    """
    API endpoint that allows stocks to be sold.
    """
    def post(self, request):
        # Get request data
        username = request.data.get("username")
        stockSymbol = request.data.get("stockSymbol")
        amount = float(request.data.get("amount"))
        price = float(request.data.get("price"))
        
        numT = Transaction.objects.all().count()
        transactionNum  = request.data.get("transactionNumber", numT)

        # Find user account
        account = Account.objects.filter(username=username).first()
        # If account is non-existing, log errorEvent to Transaction
        if account is None:
            transaction = Transaction(
                type='errorEvent',
                timestamp=int(time()*1000),
                server='DOCK1',
                transactionNum = transactionNum,
                command='SELL',
                username=username,
                stockSymbol=stockSymbol,
                amount=amount,
                errorMessage='Account does not exist.',
            )
            transaction.save()
            return Response("Account doesn't exist.", status=status.HTTP_412_PRECONDITION_FAILED)
        # Search Account for stock, log error event to transaction if doesnt exist
        stock = account.stocks.get(stockSymbol)
        if stock == None:
            transaction = Transaction(
                type='errorEvent',
                timestamp=int(time()*1000),
                server='DOCK1',
                transactionNum = transactionNum,
                command='BUY',
                username=username,
                stockSymbol=stockSymbol,
                amount=amount,
                errorMessage='Stock not owned.',
            )
            transaction.save()
            return Response("Stock not owned.", status=status.HTTP_412_PRECONDITION_FAILED)
        # Check if shares amount permit action, og error event to transaction if not 
        sharesAmount = stock['amount']
        if sharesAmount < amount:
            transaction = Transaction(
                type='errorEvent',
                timestamp=int(time()*1000),
                server='DOCK1',
                transactionNum = transactionNum,
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
                transactionNum = transactionNum + 1,
                command='SELL',
                username=username,
                stockSymbol=stockSymbol,
                amount=amount,
        )
        transaction.save()

        fun = float(account.funds)
        account.funds = fun + ( price * amount )
        account.stocks[stockSymbol]["amount"] = account.stocks[stockSymbol]["amount"] - amount
        account.stocks[stockSymbol]["totalPrice"] = account.stocks[stockSymbol]["totalPrice"] - account.stocks[stockSymbol]["avgPrice"] * amount
        
        if(account.stocks[stockSymbol]["amount"] == 0):
            del account.stocks[stockSymbol]
        
        account.save()
        

        return Response(status=status.HTTP_200_OK)
