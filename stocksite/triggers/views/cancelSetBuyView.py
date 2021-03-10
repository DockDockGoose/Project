from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from accounts.models import Account
from transactions.models import Transaction
from triggers.models import Trigger
from time import time


class CancelSetBuyView(APIView):
    """
    API endpoint that cancels a buy trigger.
    """
    def delete(self, request):
        # Get request data
        username = request.data.get("username")
        stockSymbol = request.data.get("stockSymbol")
        transactionNum = request.data.get("transactionNumber")
        command = request.data.get("command")

        # Find previous buy trigger
        trigger = Trigger.objects.filter(username=username, type='buy', stockSymbol=stockSymbol).first()
        # Find user account
        account = Account.objects.filter(username=username).first()

        # If account is non-existing, log errorEvent to Transaction
        if trigger is None:
            transaction = Transaction(
                type='errorEvent',
                timestamp=int(time()*1000),
                server='DOCK1',
                transactionNum = transactionNum,
                command=command,
                username=username,
                stockSymbol=stockSymbol,
                errorMessage='Buy trigger does not exist.',
            )
            transaction.save()
            return Response("Buy trigger doesn't exist.", status=status.HTTP_412_PRECONDITION_FAILED)

        # Add funds back into user account
        amount = trigger.amount
        account.pendingFunds -= amount
        account.funds += amount
        account.save()

        # Delete trigger
        trigger.delete()

        # Log set buy amount transaction
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

        # Also log account transaction change
        transaction = Transaction(
                type='accountTransaction',
                timestamp=int(time()*1000),
                server='DOCK1',
                transactionNum = transactionNum,
                command='add',
                username=username,
                stockSymbol=stockSymbol,
                amount=amount,
            )
        transaction.save()

        return Response(status=status.HTTP_200_OK)
