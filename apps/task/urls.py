from django.urls import path

from . import views

urlpatterns = [
    path('', views.ViewCreateTask.as_view(), name='create-task'),
    path('test/', views.Test.as_view(), name='task'),
]