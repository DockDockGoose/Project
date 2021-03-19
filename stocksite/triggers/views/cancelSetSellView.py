from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from accounts.models import Account
from transactions.models import Transaction
from triggers.models import Trigger
from .utils import getByStockSymbol
from time import time


class CancelSetSellView(APIView):
    """
    API endpoint that sets sell trigger price.
    """
    def delete(self, request):
        # Get request data
        username = request.data.get("username")
        stockSymbol = request.data.get("stockSymbol")
        transactionNum = request.data.get("transactionNumber")
        command = request.data.get("command")

        # First log cancel set sell command
        transaction = Transaction(
                type='userCommand',
                timestamp=int(time()*1000),
                server='DOCK1',
                transactionNum = transactionNum,
                command=command,
                username=username,
                stockSymbol=stockSymbol,
            )
        transaction.save()
        
        # Find previous sell trigger
        trigger = Trigger.objects.filter(username=username, type='sell', stockSymbol=stockSymbol).first()

        # If trigger is non-existing, log errorEvent to Transaction
        if trigger is None:
            transaction = Transaction(
                type='errorEvent',
                timestamp=int(time()*1000),
                server='DOCK1',
                transactionNum = transactionNum,
                command=command,
                username=username,
                stockSymbol=stockSymbol,
                errorMessage='Sell trigger does not exist.',
            )
            transaction.save()
            return Response("Sell trigger does not exist.", status=status.HTTP_412_PRECONDITION_FAILED)

        # Decrease the number of stock shares in user's account 
        account = Account.objects.filter(username=username).first()
        stock = getByStockSymbol(account.stocks, stockSymbol)
        stock['sharesAmount'] += trigger.sharesAmount * trigger.price

        account.save()

        # Delete trigger
        trigger.delete()

        # Also log account transaction change
        transaction = Transaction(
                type='accountTransaction',
                timestamp=int(time()*1000),
                server='DOCK1',
                transactionNum = transactionNum,
                action='add',
                username=username,
                stockSymbol=stockSymbol,
                amount=trigger.sharesAmount * trigger.price,
            )
        transaction.save()

        return Response(status=status.HTTP_200_OK)
