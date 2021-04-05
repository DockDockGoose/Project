from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from transactions.models import Transaction
from transactions.serializers import TransactionSerializer
from triggers.models import Trigger
from triggers.serializers import TriggerSerializer
from .models import Account
from .serializers import AccountSerializer
from time import time

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from accounts.models import Account
from triggers.models import Trigger
from time import time

"""
    TODO: 
        - Need to uncomment the dumplog response that returns all transaction
        (Commented out to save time)
"""

# TODO: Implement Account view logic (change id to UUID), transaction tracking & server mapping

class AccountListView(APIView):
    """
    API endpoint that lists accounts to be viewed or edited.
    """
    def get(self, request):
        all_Accounts = Account.objects.all()
        serializer = AccountSerializer(all_Accounts, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

# class AccountView(APIView):
#     """
#     API endpoint that allows a single account to be viewed.
#     """

#     def get(self, request, username):
#         """
#         Get account data.
#         """
#         #  Responses with HTTP 404 if Account doesnt exist. 
#         # TODO: Figure out how to make dynamic account urls using this
#         # account = get_object_or_404(Account, userId=self.kwargs['userId'])

#         username = request.data.get("username")

#         # Find account
#         account = Account.objects.filter(username=username,).first()

#         # Serialize data for serving
#         serializer = AccountSerializer(account)

#         # Log systemEvent using Transaction model (create data obj & .save())

#         return Response(serializer.data, status=status.HTTP_200_OK)
    

class AddView(APIView):
    def post(self, request):
        """
        Add funds to a new or existing account.
        """
        username = request.data.get("username")
        amount = request.data.get("amount")
        command = request.data.get("command")
        transactionNum = request.data.get("transactionNum")

        # First thing log the command
        transaction = Transaction(
                type='userCommand',
                timestamp=int(time()*1000),
                server='DOCK1',
                transactionNum= transactionNum,
                command=command,
                username=username,
                amount=amount,
            )
        transaction.save()

        if amount is None:
            amount = 0.00
        else:
            amount = float(request.data.get("amount"))

        # Find account
        account = Account.objects.filter(username=username).first()

        # Create if non-existing
        if account is None:
            account = Account(username=username, funds=0.00)

        account.funds += amount
        # Test stock values (uncomment to populate the db) - remove later
        # account.stocks = [{'stockSymbol':"NISSAN", 'sharesAmount':250, 'quoteServerTime':int(time()*1000), 'price': 3.50},{'stockSymbol':"TESLA", 'sharesAmount':20.50, 'quoteServerTime':int(time()*1000), 'price': 2.50} ]
        account.save()

        # Log accountTransaction event using Transaction model (create data obj * .save())
        accountTransaction = Transaction(
            type="accountTransaction",
            timestamp=int(time()*1000),
            server='DOCK1',
            transactionNum=transactionNum,
            action='add',
            username=username,
            amount=amount
        )

        accountTransaction.save()

        return Response(status=status.HTTP_200_OK)

class DumplogView(APIView):
    """
    API endpoint for dumping all logs or logs of a given user.
    """
    def get(self, request):
        username = request.data.get("username")
        command = request.data.get("command")
        transactionNum = request.data.get("transactionNum")

        # First thing log the command
        transaction = Transaction(
                type='userCommand',
                timestamp=int(time()*1000),
                server='DOCK1',
                transactionNum= transactionNum,
                command=command,
                username=username,
            )
        transaction.save()

        # Check if commmand had a user with it, else print all commands
        if username is None:
            transactions = Transaction.objects.filter()
        else:
            transactions = Transaction.objects.filter(username=username)
            serializer = TransactionSerializer(transactions)

        serializer = TransactionSerializer(transactions)

        #return Response(serializer.data, status=status.HTTP_200_OK)

        return Response(status=status.HTTP_200_OK)

class DisplaySummary(APIView):
    """
    API endpoint that displays all of an users transactions, stocks, and triggers.
    """
    def get(self, request):
        username = request.data.get("username")
        command = request.data.get("command")
        transactionNum = request.data.get("transactionNum")
        # First thing log the command
        transaction = Transaction(
                type='userCommand',
                timestamp=int(time()*1000),
                server='DOCK1',
                transactionNum= transactionNum,
                command=command,
                username=username,
            )
        transaction.save()

        # Get users transaction, account, and triggers
        user_transactions = Transaction.objects.filter(username=username)
        user_account = Account.objects.filter(username=username).first()
        #user_triggers = Trigger.objects.filter(username=username)

        # Serialize the data and send back response
        
        # transactions_serializer = TransactionSerializer(user_transactions)
        # triggers_serializer = TriggerSerializer(user_triggers)
        # account_serializer = AccountSerializer(user_account)

        # TODO: Add all the data together and send back to user

        result = "Data"

        return Response(result, status=status.HTTP_200_OK)
