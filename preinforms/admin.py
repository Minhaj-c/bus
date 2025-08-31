from django.contrib import admin
from .models import PreInform

@admin.register(PreInform)
class PreInformAdmin(admin.ModelAdmin):
    list_display = ('user', 'route', 'date_of_travel', 'desired_time', 'boarding_stop', 'passenger_count', 'status', 'created_at')
    list_filter = ('status', 'date_of_travel', 'route')
    search_fields = ('user__email', 'route__number', 'boarding_stop__name')
    list_editable = ('status',)
    raw_id_fields = ('user', 'route', 'boarding_stop')