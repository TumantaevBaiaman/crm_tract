from django.urls import path

from apps.account.views import AccountView

urlpatterns = [
    path('account/', AccountView.as_view(), name='get-account'),
]