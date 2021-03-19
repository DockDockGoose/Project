from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from transactions.models import Transaction
from triggers.models import Trigger
from time import time


class SetBuyTriggerView(APIView):
    """
    API endpoint that sets buy price triggers.
    """
    def put(self, request):
        # Get request data
        username = request.data.get("username")
        stockSymbol = request.data.get("stockSymbol")
        amount = float(request.data.get("amount"))
        transactionNum = request.data.get("transactionNumber")
        command = request.data.get("command")

        # First log set buy trigger
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

        # Find previous buy trigger
        trigger = Trigger.objects.filter(username=username, type='buy', stockSymbol=stockSymbol).first()

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
                amount=amount,
                errorMessage='Buy trigger does not exist.',
            )
            transaction.save()
            return Response("Buy trigger doesn't exist.", status=status.HTTP_412_PRECONDITION_FAILED)

        # Update trigger to include trigger price
        trigger.price = amount
        trigger.save()

        return Response(status=status.HTTP_200_OK)
