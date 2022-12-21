from django.urls import path
from .views import (
    ViewCustomer, ViewGetCustomers, ViewAllCustomers
)

urlpatterns = [
    path('', ViewCustomer.as_view(), name='create-customer'),
    path('empl-customers/', ViewGetCustomers.as_view(), name='get-customers'),
    path('all-customers/', ViewAllCustomers.as_view(), name='get-all-customers'),
]