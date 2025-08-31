from django.urls import path
from . import views

urlpatterns = [
    path('admin-dashboard/', views.admin_dashboard, name='admin-dashboard'),
    path('generate-report/', views.generate_weekly_report_view, name='generate-report'),
    # ONLY include URLs for operations app views here
    # Remove the line with 'demand-alert/' as it belongs to the demand app
]