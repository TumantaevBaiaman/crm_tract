from django.shortcuts import render
from . models import ModelsSatus
from rest_framework.authentication import SessionAuthentication, BasicAuthentication
from rest_framework.permissions import IsAuthenticated, IsAdminUser, AllowAny
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from .serializers import SerializerRegisterUser, SerializerRegisterAccount
from .logic.logic import CreateAccount, CreateUser
from apps.account.serializers import SerializerCreateAccount
from .logic.request_data import request_data_user, request_data_account


class ViewRegisterAccount(APIView):
    authentication_classes = [SessionAuthentication, BasicAuthentication]
    permission_classes = [AllowAny]

    def post(self, request, format=None):
        request_data = request.data
        data_account = request_data_account(request_data)
        data_user = request_data_user(request_data)

        serializer_account = SerializerCreateAccount(data=data_account)
        serializer_user = SerializerRegisterAccount(data=data_user)
        if serializer_user.is_valid() and serializer_account.is_valid():
            data_create = CreateAccount(data_user=data_user, data_account=data_account)
            data_create.create()
            return Response(serializer_user.data, status=status.HTTP_201_CREATED)
        return Response(serializer_user.errors, status=status.HTTP_400_BAD_REQUEST)


class ViewRegisterUser(APIView):

    authentication_classes = [SessionAuthentication, BasicAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request, format=None):
        request_user, request_data = request.user, request.data
        serializer_user = SerializerRegisterUser(data=request_data)
        account = request_user.account_id

        request_data['account_id'] = account.id
        request_data['status'] = ModelsSatus.objects.get(name='customer').id

        if serializer_user.is_valid() and request_user.status.name == 'admin':
            data_create = CreateUser(request_data)
            data_create.create()
            return Response(serializer_user.data, status=status.HTTP_201_CREATED)
        elif serializer_user.is_valid() and request_user.status != 'admin':
            return Response(status=status.HTTP_401_UNAUTHORIZED)
        return Response(serializer_user.errors, status=status.HTTP_400_BAD_REQUEST)




