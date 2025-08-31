from django.urls import path
from . import views

urlpatterns = [
    path('schedules/', views.schedules_page, name='schedules-page'),
    path('api/schedules/', views.ScheduleListView.as_view(), name='schedule-list'),
]