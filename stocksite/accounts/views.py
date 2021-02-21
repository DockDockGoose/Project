from django.shortcuts import render
from rest_framework.generics import ListAPIView
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django_filters.rest_framework import DjangoFilterBackend
from .models import Account
from .serializers import AccountSerializer

# TODO: Implement Account view logic

class AccountListView(ListAPIView):
    """
    API endpoint that lists accounts to be viewed or edited.
    """
    queryset = Account.objects.all()
    serializer_class = AccountSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['userId']
    

class AddView(APIView):
    """
    API endpoint that allows funds to be viewed or added to accounts.
    """
    def get(self, request):
        """
        Get account data.
        """
        userId = request.data.get("userId")

        # Find account
        account = Account.objects.filter(userId=userId,).first()

        # Serialize data for serving
        serializer = AccountSerializer(account)

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
        
        return Response(status=status.HTTP_200_OK)
