from django.contrib import admin
from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView

from . import views

urlpatterns = [
    path('create/', views.ViewCreateInvoice.as_view(), name='create-invoice'),
]