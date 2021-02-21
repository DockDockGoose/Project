from django.shortcuts import render, get_object_or_404
from rest_framework.generics import ListAPIView
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django_filters.rest_framework import DjangoFilterBackend
from transactions.models import Transaction
from .models import Account
from .serializers import AccountSerializer
from time import time

# TODO: Implement Account view logic (change id to UUID), transaction tracking & server mapping

class AccountListView(ListAPIView):
    """
    API endpoint that lists accounts to be viewed or edited.
    """
    queryset = Account.objects.all()
    serializer_class = AccountSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['userId']

class AccountView(APIView):
    """
    API endpoint that allows a single account to be viewed.
    """

    def get(self, request, userId):
        """
        Get account data.
        """
        #  Responses with HTTP 404 if Account doesnt exist. 
        # TODO: Figure out how to make dynamic account urls using this
        # account = get_object_or_404(Account, userId=self.kwargs['userId'])

        userId = request.data.get("userId")

        # Find account
        account = Account.objects.filter(userId=userId,).first()

        # Serialize data for serving
        serializer = AccountSerializer(account)

        # Log systemEvent using Transaction model (create data obj & .save())

        return Response(serializer.data, status=status.HTTP_200_OK)
    

class AddView(APIView):
    """
    API endpoint that allows funds to be viewed or added to accounts.
    """
    def get(self, request):
        """
        Get account & funds data.
        """
        userId = request.data.get("userId")

        # Find account
        account = Account.objects.filter(userId=userId,).first()

        # Serialize data for serving
        serializer = AccountSerializer(account)

        #L Log systemEvent using Transaction model (create data obj & .save())

        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        """
        Add funds to a new or existing account.
        """
        userId = request.data.get("userId")
        amount = float(request.data.get("amount"))

        # Find account
        account = Account.objects.filter(userId=userId,).first()

        # Create if non-existing
        if account is None:
            account = Account(userId=userId)

        account.funds += amount
        account.save()

        # Log accountTransaction event using Transaction model (create data obj * .save())
        accountTransaction = Transaction(
            type="accountTransaction",
            timestamp=int(time()*1000),
            server='DOCK1',
            transactionNum=0,
            command='add',
            userId=userId,
            amount=amount
        )

        accountTransaction.save()

        return Response(status=status.HTTP_200_OK)
