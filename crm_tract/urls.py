from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include
from crm_tract import settings

urlpatterns = [
    path('admin/', admin.site.urls),
    path('apps/users/', include('apps.users.urls')),
    path('apps/cars/', include('apps.cars.urls')),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
