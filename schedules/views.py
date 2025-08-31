from rest_framework import generics
from django.utils import timezone
from django.shortcuts import render, redirect  # <-- ADD redirect HERE
from django.contrib.auth.decorators import user_passes_test  # <-- ADD THIS IMPORT
from .models import Schedule, Bus, Route, BusSchedule  # <-- ADD Bus, Route, BusSchedule
from .serializers import ScheduleSerializer

# KEEP ALL EXISTING CODE - API VIEWS
class ScheduleListView(generics.ListAPIView):
    """API view to list schedules, optionally filtered by route and date."""
    serializer_class = ScheduleSerializer

    def get_queryset(self):
        queryset = Schedule.objects.all().select_related('route', 'bus')
        
        # Get filter parameters from the URL query string
        route_id = self.request.query_params.get('route_id', None)
        date = self.request.query_params.get('date', None)
        
        # Apply filters if they are provided
        if route_id:
            queryset = queryset.filter(route_id=route_id)
        if date:
            queryset = queryset.filter(date=date)
        else:
            # If no date is provided, default to today and future schedules
            today = timezone.now().date()
            queryset = queryset.filter(date__gte=today)
        
        return queryset.order_by('date', 'departure_time')

# KEEP EXISTING PAGE VIEW
def schedules_page(request):
    """Serve the schedules frontend page"""
    route_id = request.GET.get('route_id')
    context = {'route_id': route_id}
    return render(request, 'schedules.html', context)

# NEW VIEW ADDED BELOW - DO NOT REMOVE EXISTING CODE ABOVE
def admin_check(user):
    return user.is_authenticated and user.role == 'admin'

@user_passes_test(admin_check)
def create_bus_schedule(request):
    """View for creating bus schedule assignments (operational planning)"""
    if request.method == 'POST':
        bus_id = request.POST.get('bus')
        route_id = request.POST.get('route')
        date = request.POST.get('date')
        start_time = request.POST.get('start_time')
        end_time = request.POST.get('end_time')
        
        bus = Bus.objects.get(id=bus_id)
        route = Route.objects.get(id=route_id)
        
        # Create the bus schedule assignment
        BusSchedule.objects.create(
            bus=bus,
            route=route,
            date=date,
            start_time=start_time,
            end_time=end_time
        )
        return redirect('create-bus-schedule')
    
    buses = Bus.objects.all()
    routes = Route.objects.all()
    schedules = BusSchedule.objects.all().select_related('bus', 'route').order_by('-date', 'start_time')
    
    return render(request, 'create_schedule.html', {
        'buses': buses,
        'routes': routes,
        'schedules': schedules
    })