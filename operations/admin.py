from django.contrib import admin
from .models import WeeklyPerformance

@admin.register(WeeklyPerformance)
class WeeklyPerformanceAdmin(admin.ModelAdmin):
    list_display = ('bus', 'route', 'week_start_date', 'total_passengers', 'total_kms', 'total_profit')
    list_filter = ('week_start_date', 'route', 'bus')
    search_fields = ('bus__number_plate', 'route__number')