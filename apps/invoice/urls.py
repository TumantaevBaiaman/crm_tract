from django.urls import path

from . import views

urlpatterns = [
    path('', views.ViewGetInvoice.as_view(), name='invoice'),
    path('export-list/', views.InvoiceListExport.as_view(), name='invoice-list-export'),
    path('export/', views.InvoiceExport.as_view(), name='invoice-export'),
    path('export-csv/', views.InvoiceExportCSV.as_view(), name='invoice-export-csv'),
]
