from django.urls import path
from . import views

urlpatterns = [
    path('schedules/', views.schedules_page, name='schedules-page'),
    path('api/schedules/', views.ScheduleListView.as_view(), name='schedule-list'),
    path('create-schedule/', views.create_bus_schedule, name='create-bus-schedule'),
    path('api/buses/nearby/', views.nearby_buses, name='nearby-buses'),
    path('api/buses/update-location/', views.update_bus_location, name='update-bus-location'),
    path('api/buses/<int:bus_id>/', views.bus_details, name='bus-details'),
    path('api/buses/nearby/', views.nearby_buses, name='nearby-buses'),
]