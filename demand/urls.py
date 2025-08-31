from django.urls import path
from . import views

urlpatterns = [
    path('demand-alert/', views.demand_alert_page, name='demand-alert-page'),
    path('api/demand-alerts/', views.DemandAlertCreateView.as_view(), name='demand-alert-create'),
]