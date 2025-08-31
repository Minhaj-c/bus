from django.contrib import admin
from .models import DemandAlert

@admin.register(DemandAlert)
class DemandAlertAdmin(admin.ModelAdmin):
    list_display = ('user', 'stop', 'number_of_people', 'status', 'created_at', 'expires_at', 'is_active')
    list_filter = ('status', 'stop', 'created_at')
    search_fields = ('user__email', 'stop__name')
    list_editable = ('status',)
    readonly_fields = ('created_at', 'expires_at')