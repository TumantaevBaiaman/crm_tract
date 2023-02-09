from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView

from .views import (
    ViewRegisterAccount,
    ViewRegisterUser, LoginView,
    ViewListUser, ViewListStatus, ProfileView, ViewRegisterNewUser
)

urlpatterns = [
    path('register/account/', ViewRegisterAccount.as_view(), name='register-account'),
    path('register/user/', ViewRegisterUser.as_view(), name='register-user'),
    path('register/profile/', ViewRegisterNewUser.as_view(), name='register-profile'),
    path('login/', LoginView.as_view(), name='token'),
    path('refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('user_list/', ViewListUser.as_view(), name='employee-list'),
    path('status_list/', ViewListStatus.as_view(), name='status-list'),
    path('profile/', ProfileView.as_view(), name='profile'),
]