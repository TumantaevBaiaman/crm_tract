from django.urls import path

from apps.account.views import AccountView, AccountUpdateView

urlpatterns = [
    path('account/', AccountView.as_view(), name='get-account'),
    path('account-update/', AccountUpdateView.as_view(), name='update-account'),
]