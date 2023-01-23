from django.urls import path

from . import views

urlpatterns = [
    path('', views.ViewGetInvoice.as_view(), name='invoice'),
    path('export/', views.InvoiceExport.as_view(), name='invoice-export'),
]
