from django.http import Http404
from django.shortcuts import render
from rest_framework import status
from rest_framework.authentication import SessionAuthentication, BasicAuthentication
from rest_framework.permissions import IsAdminUser, IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from apps.users import models as models_user

from . import models
from . import serializers
from . import logic


class ViewCreateCar(APIView):
    authentication_classes = [SessionAuthentication, BasicAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request, format=None):
        try:
            data = logic.extract_request_data(request)
            serializer = serializers.SerializerCreateCar(data=data)
            print(data)
            if serializer.is_valid():
                logic.create_car(serializer.data)
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except BaseException as ex:
            return Response({
                'success': False,
            }, status=status.HTTP_400_BAD_REQUEST)