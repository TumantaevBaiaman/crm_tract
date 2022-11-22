from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include
from crm_tract import settings

urlpatterns = [
    path('admin/', admin.site.urls, name='admin'),
    path('apps/users/', include('apps.users.urls'), name='users'),
    path('apps/cars/', include('apps.cars.urls'), name='cars'),
    path('apps/customers/', include('apps.customer.urls'), name='customers'),
    path('apps/invoices/', include('apps.invoice.urls'),  name='invoices'),
    path('apps/tasks/', include('apps.task.urls'), name='tasks')
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
