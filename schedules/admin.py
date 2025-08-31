from django.contrib import admin
from .models import Bus, Schedule

@admin.register(Bus)
class BusAdmin(admin.ModelAdmin):
    list_display = ('number_plate', 'capacity', 'is_active')
    list_filter = ('is_active',)
    search_fields = ('number_plate',)

@admin.register(Schedule)
class ScheduleAdmin(admin.ModelAdmin):
    # Fields to display in the list view
    list_display = ('route', 'date', 'departure_time', 'bus', 'driver', 'available_seats', 'total_seats')
    # Adds filters for date, route, etc.
    list_filter = ('date', 'route', 'bus')
    # Adds a search box
    search_fields = ('route__number', 'bus__number_plate', 'driver__email')
    # Drop-down filters for better UX
    raw_id_fields = ('route', 'bus', 'driver')

    # This is a powerful feature: show available seats right in the list
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('route', 'bus', 'driver')