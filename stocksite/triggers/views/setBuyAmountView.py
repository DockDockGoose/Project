from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from accounts.models import Account
from transactions.models import Transaction
from triggers.models import Trigger
from time import time


class SetBuyAmountView(APIView):
    """
    API endpoint that sets buy amount triggers.
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
                errorMessage='Account does not exist for buy trigger.',
            )
            transaction.save()
            return Response("Account doesn't exist for buy trigger.", status=status.HTTP_412_PRECONDITION_FAILED)

        # Check if funds permit action, log error event to transaction if not
        if account.funds < amount:
            transaction = Transaction(
                type='errorEvent',
                timestamp=int(time()*1000),
                server='DOCK1',
                transactionNum = transactionNum,
                command=command,
                username=username,
                stockSymbol=stockSymbol,
                amount=amount,
                errorMessage='Insufficient funds for buy trigger :(.',
            )
            transaction.save()
            return Response("Insufficient funds for buy trigger :(.", status=status.HTTP_412_PRECONDITION_FAILED)

        # Add new trigger buy command and remove funds from account
        trigger = Trigger(username=username, type='buy', stockSymbol=stockSymbol, amount=amount)
        trigger.save()

        # Remove funds from user account and put into pending
        account.funds -= amount
        account.pendingFunds += amount
        account.save()

        # Log set buy amount transaction
        transaction = Transaction(
                type='userCommand',
                timestamp=int(time()*1000),
                server='DOCK1',
                transactionNum = transactionNum,
                command=command,
                username=username,
                stockSymbol=stockSymbol,
                amount=amount,
            )
        transaction.save()

        # Also log account transaction change
        transaction = Transaction(
                type='accountTransaction',
                timestamp=int(time()*1000),
                server='DOCK1',
                transactionNum = transactionNum,
                command='remove',
                username=username,
                stockSymbol=stockSymbol,
                amount=amount,
            )
        transaction.save()

        return Response(status=status.HTTP_200_OK)
