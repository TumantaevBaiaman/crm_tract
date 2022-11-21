from django.http import Http404
from django.shortcuts import render
from rest_framework import status
from rest_framework.authentication import SessionAuthentication, BasicAuthentication
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from apps.users import models as models_user

from . import models
from . import serializers


class ViewCreateCar(APIView):

    def post(self, request, format=None):
        pass