from django.http import Http404
from django.shortcuts import render
from rest_framework import status
from rest_framework.authentication import SessionAuthentication, BasicAuthentication
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from apps.users import models as models_user

from . import models
from .serializers import (
    SerializerCreateCar,
    SerializerCar
)


class ViewCreateCar(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, format=None):
        info_user = models_user.ModelsUser.objects.get(id=request.user.id)
        print(info_user)
        if info_user.status == 'customer' or info_user.is_admin == True:
            serializer = SerializerCreateCar(data=request.data)
            if serializer.is_valid():
                car = models.ModelsCars.objects.create(
                    customer_id=request.user.id,
                    description=request.data['description'],
                    vin=request.data['vin'],
                    model=request.data['model'],
                    image=request.data['image']
                )
                car.save()
                return Response(request.data, status=status.HTTP_201_CREATED)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        elif info_user.status != 'customer' or info_user.is_admin != True:
            return Response({'INFO': 'ERROR UNAUTHORIZED '}, status=status.HTTP_401_UNAUTHORIZED)


class ViewListCars(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, requests):
        cars = models.ModelsCars.objects.all()
        serializer = SerializerCar(cars, many=True)
        return Response(serializer.data)


class ViewUpdateCars(APIView):
    permission_classes = [IsAuthenticated]

    def get_objects(self, pk):
        try:
            return models.ModelsCars.objects.get(pk=pk)
        except models.ModelsCars.DoesNotExist:
            raise Http404

    def put(self, request, pk, format=None):
        cars = self.get_objects(pk)
        serializer = SerializersCars(cars)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# if info_user.status == 'customer' or info_user.is_admin == True:
#     car = models.ModelsCars.objects.create(
#         customer_id=request.data['customer'],
#         description=request.data['description'],
#         vin=request.data['vin'],
#         model=request.data['model'],
#         image=request.data['image']
#     )
#     car.save()