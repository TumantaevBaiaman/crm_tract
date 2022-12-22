from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from . import serializers
from .logic import (
    create_customer, get_customers,
    get_all_customers, update_customers,
    delete_customers
)


class ViewCustomer(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        return create_customer(request)


class ViewGetCustomers(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        return get_customers(request)

    def put(self, request):
        return update_customers(request)

    def delete(self, request):
        return delete_customers(request)


class ViewAllCustomers(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        return get_all_customers(request)
