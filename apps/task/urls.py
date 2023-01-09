from django.urls import path

from . import views

urlpatterns = [
    path('', views.ViewCreateTask.as_view(), name='create-task'),
    path('get-tasks/', views.ViewGetTask.as_view(), name='get-tasks'),
]