from django.contrib import admin
from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView

from . import views

urlpatterns = [
    path('', views.ViewCar.as_view(), name='car'),
    path('empl-car/', views.ViewGetCar.as_view(), name='get-car'),
]