from django.urls import path

from . import views

urlpatterns = [
    path('', views.ViewCar.as_view(), name='car'),
    path('empl-car/', views.ViewGetCar.as_view(), name='get-car'),
    path('update-car/', views.ViewUpdateCar.as_view(), name='get-car'),
    path('delete-car/', views.ViewDeleteCar.as_view(), name='get-car'),
]