from django.urls import path
from . import views

urlpatterns = [
    path('api/demand-alerts/', views.DemandAlertCreateView.as_view(), name='demand-alert-create'),
]