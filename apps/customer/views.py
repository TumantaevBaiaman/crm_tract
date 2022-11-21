from django.shortcuts import render
from rest_framework import status
from rest_framework.authentication import SessionAuthentication, BasicAuthentication
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from . import logic
from . import serializers


class ViewCreateCustomer(APIView):
    authentication_classes = [SessionAuthentication, BasicAuthentication]
    permission_classes = [AllowAny]

    def post(self, request, format=None):
        try:
            data = logic.extract_request_data(request)
            serializer = serializers.SerializerCreateCustomer(data=data)
            if serializer.is_valid():
                logic.create_customer(serializer.data)
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except BaseException as ex:
            print(ex)
            return Response({
                'success': False,
            }, status=status.HTTP_400_BAD_REQUEST)
