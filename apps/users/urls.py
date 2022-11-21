from django.contrib import admin
from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView

from .views import (
    ViewRegisterAccount,
    ViewRegisterUser
)

urlpatterns = [
    path('register/account/', ViewRegisterAccount.as_view(), name='register-account'),
    path('register/user/', ViewRegisterUser.as_view(), name='register-user'),
    path('login/', TokenObtainPairView.as_view(), name='token'),
]