from django.urls import path
from . import views

urlpatterns = [
    path('api/schedules/', views.ScheduleListView.as_view(), name='schedule-list'),
]