from django.urls import path
from . import views

urlpatterns = [
    path('', views.api_welcome, name='api-welcome'),
    path('api/routes/', views.RouteListView.as_view(), name='route-list'),
]