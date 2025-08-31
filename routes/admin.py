from django.contrib import admin
from .models import Route, Stop

# Allows adding Stops directly from the Route admin page
class StopInline(admin.TabularInline):
    model = Stop
    extra = 1 # Shows 1 empty stop form by default

# Customize how the Route model looks in the admin
class RouteAdmin(admin.ModelAdmin):
    # Fields to display in the list view
    list_display = ('number', 'name', 'origin', 'destination', 'total_distance')
    # Adds a search box
    search_fields = ('number', 'name', 'origin', 'destination')
    # Adds filters on the right side
    list_filter = ('origin', 'destination')
    # Show the Stop forms inline
    inlines = [StopInline]

# Register both models
admin.site.register(Route, RouteAdmin)
admin.site.register(Stop)