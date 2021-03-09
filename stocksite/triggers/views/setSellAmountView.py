from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from accounts.models import Account
from transactions.models import Transaction
from .models import Trigger
from .utils import getByStockSymbol
from time import time


class SetSellAmountView(APIView):
    """
    API endpoint that sets sell trigger amounts.
    """
    def post(self, request):
        # Get request data
        username = request.data.get("username")
        stockSymbol = request.data.get("stockSymbol")
        amount = float(request.data.get("amount"))
        transactionNum = request.data.get("transactionNumber")
        command = request.data.get("command")

        # Find user account
        account = Account.objects.filter(username=username).first()

        # If account is non-existing, log errorEvent to Transaction
        if account is None:
            transaction = Transaction(
                type='errorEvent',
                timestamp=int(time()*1000),
                server='DOCK1',
                transactionNum = transactionNum,
                command=command,
                username=username,
                stockSymbol=stockSymbol,
                amount=amount,
                errorMessage='Account does not exist.',
            )
            transaction.save()
            return Response("Account doesn't exist.", status=status.HTTP_412_PRECONDITION_FAILED)

        # Get stock from user
        stock = getByStockSymbol(account.stocks, stockSymbol)

        # If user does not have the stock
        if stock is None:
            transaction = Transaction(
                type='errorEvent',
                timestamp=int(time()*1000),
                server='DOCK1',
                transactionNum = transactionNum,
                command=command,
                username=username,
                stockSymbol=stockSymbol,
                amount=amount,
                errorMessage='User does not have the stock.',
            )
            transaction.save()
            return Response("User does not have the stock.", status=status.HTTP_412_PRECONDITION_FAILED)

        # Check if funds permit action, log error event to transaction if not
        if stock['sharesAmount'] < amount:
            transaction = Transaction(
                type='errorEvent',
                timestamp=int(time()*1000),
                server='DOCK1',
                transactionNum = transactionNum,
                command=command,
                username=username,
                stockSymbol=stockSymbol,
                amount=amount,
                errorMessage='Insufficient amount of stock :(.',
            )
            transaction.save()
            return Response("Insufficient amount of stock :(.", status=status.HTTP_412_PRECONDITION_FAILED)

        # Add new trigger sell command
        trigger = Trigger(username=username, type='sell', stockSymbol=stockSymbol, amount=amount)
        trigger.save()

        # Log buy transaction
        transaction = Transaction(
                type='userCommand',
                timestamp=int(time()*1000),
                server='DOCK1',
                transactionNum = transactionNum + 1,
                command=command,
                username=username,
                stockSymbol=stockSymbol,
                amount=amount,
            )
        transaction.save()

        return Response(status=status.HTTP_200_OK)
