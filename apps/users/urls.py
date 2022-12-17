from django.urls import path

from .views import (
    ViewRegisterAccount,
    ViewRegisterUser, LoginView,
    ViewListUser
)

urlpatterns = [
    path('register/account/', ViewRegisterAccount.as_view(), name='register-account'),
    path('register/user/', ViewRegisterUser.as_view(), name='register-user'),
    path('login/', LoginView.as_view(), name='token'),
    path('user_list/', ViewListUser.as_view(), name='employee-list'),

]