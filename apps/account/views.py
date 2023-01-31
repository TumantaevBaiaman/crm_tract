from django.shortcuts import render
from rest_framework import permissions
from rest_framework.views import APIView

from apps.account.logic import get_account, get_update_account


class AccountView(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request):
        return get_account(request.user, request.data)


class AccountUpdateView(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request):
        return get_update_account(request)
