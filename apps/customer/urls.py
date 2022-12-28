from django.urls import path
from .views import (
    ViewCustomer, ViewGetCustomers, ViewAllCustomers, ViewUpdateCustomers, ViewDeleteCustomers
)

urlpatterns = [
    path('', ViewCustomer.as_view(), name='create-customer'),
    path('empl-customers/', ViewGetCustomers.as_view(), name='get-customers'),
    path('update-customers/', ViewUpdateCustomers.as_view(), name='update-customers'),
    path('delete-customers/', ViewDeleteCustomers.as_view(), name='delete-customers'),
    path('all-customers/', ViewAllCustomers.as_view(), name='get-all-customers'),
]