from django.contrib import admin
from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView

from .views import (
    ViewCreateCustomer
)

urlpatterns = [
    path('create/', ViewCreateCustomer.as_view(), name='register-account'),
]