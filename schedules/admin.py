from django.contrib import admin
from .models import Bus, Schedule, BusSchedule

@admin.register(Bus)
class BusAdmin(admin.ModelAdmin):
    list_display = (
        'number_plate', 'capacity', 'is_active', 'is_running',
        'current_route', 'last_location_update'
    )
    list_filter = ('is_active', 'is_running', 'service_type')
    search_fields = ('number_plate',)
    readonly_fields = ('last_location_update',)
    
    fieldsets = (
        ('Basic Info', {
            'fields': ('number_plate', 'capacity', 'mileage', 'service_type', 'is_active')
        }),
        ('Real-time Tracking', {
            'fields': (
                'is_running', 'current_route',
                'current_latitude', 'current_longitude', 'last_location_update'
            )
        })
    )

@admin.register(Schedule)
class ScheduleAdmin(admin.ModelAdmin):
    list_display = ('route', 'date', 'departure_time', 'bus', 'driver', 'available_seats', 'total_seats')
    list_filter = ('date', 'route', 'bus')
    search_fields = ('route__number', 'bus__number_plate', 'driver__email')
    raw_id_fields = ('route', 'bus', 'driver')

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('route', 'bus', 'driver')

@admin.register(BusSchedule)
class BusScheduleAdmin(admin.ModelAdmin):
    list_display = ('bus', 'route', 'date', 'start_time', 'end_time', 'duration_hours')
    list_filter = ('date', 'bus', 'route')
    search_fields = ('bus__number_plate', 'route__number')
    date_hierarchy = 'date'