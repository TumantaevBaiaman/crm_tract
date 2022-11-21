from django.contrib import admin
from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView

from .views import ViewCreateCar, ViewListCars

urlpatterns = [
    path('create/', ViewCreateCar.as_view(), name='register'),
    path('all/', ViewListCars.as_view(), name='all_cars'),
]