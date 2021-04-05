from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from accounts.models import Account
from transactions.models import Transaction
from time import time


class BuyView(APIView):
    """
    API endpoint that allows stocks to be bought.
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

        totalPrice = amount * price
        # If account is non-existing, log errorEvent to Transaction
        if account is None:
            transaction = Transaction(
                type='errorEvent',
                timestamp=int(time()*1000),
                server='DOCK1',
                transactionNum = transactionNum,
                command='BUY',
                username=username,
                stockSymbol=stockSymbol,
                amount=amount,
                errorMessage='Account does not exist.',
            )
            transaction.save()
            return Response("Account doesn't exist.", status=status.HTTP_412_PRECONDITION_FAILED)
        
        # Check if funds permit action, log error event to transaction if not
        if account.funds < totalPrice:
            transaction = Transaction(
                type='errorEvent',
                timestamp=int(time()*1000),
                server='DOCK1',
                transactionNum = transactionNum,
                command='BUY',
                username=username,
                stockSymbol=stockSymbol,
                amount=amount,
                errorMessage='Insufficient funds :(.',
            )
            transaction.save()
            return Response("Insufficient funds :(.", status=status.HTTP_412_PRECONDITION_FAILED)
        
        # Log buy transaction
        transactionNum = int(transactionNum + 1)
        transaction = Transaction(
                type='userCommand',
                timestamp=int(time()*1000),
                server='DOCK1',
                transactionNum = transactionNum,
                command='BUY',
                username=username,
                stockSymbol=stockSymbol,
                amount=amount,
                price=price
            )
        
        transaction.save()

        fun = float(account.funds)
        account.funds = fun - totalPrice

        if(not account.stocks):
            account.stocks[stockSymbol] = {"totalPrice": totalPrice, "amount": amount, "avgPrice": price}
        else:
            if(stockSymbol in account.stocks):
                account.stocks[stockSymbol]["totalPrice"] = account.stocks[stockSymbol]["totalPrice"] + totalPrice
                account.stocks[stockSymbol]["amount"] = account.stocks[stockSymbol]["amount"] + amount
                account.stocks[stockSymbol]["avgPrice"] = account.stocks[stockSymbol]["totalPrice"] / account.stocks[stockSymbol]["amount"]

            else:
                account.stocks[stockSymbol] = {"totalPrice": totalPrice, "amount": amount, "avgPrice": price}
        
        account.save()
        return Response(status=status.HTTP_200_OK)
