from rest_framework import generics
from django.utils import timezone
from django.shortcuts import render, redirect  # <-- ADD redirect HERE
from django.contrib.auth.decorators import user_passes_test  # <-- ADD THIS IMPORT
from .models import Schedule, Bus, Route, BusSchedule  # <-- ADD Bus, Route, BusSchedule
from .serializers import ScheduleSerializer
from django.db.models import Q
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from datetime import timedelta
import math
from .serializers import LiveBusSerializer,BusLocationSerializer

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
class ScheduleListView(generics.ListAPIView):
    serializer_class = ScheduleSerializer

    def get_queryset(self):
        queryset = Schedule.objects.all().select_related('route', 'bus')
        
        route_id = self.request.query_params.get('route_id', None)
        date = self.request.query_params.get('date', None)
        
        if route_id:
            queryset = queryset.filter(route_id=route_id)
        if date:
            queryset = queryset.filter(date=date)
        else:
            today = timezone.now().date()
            queryset = queryset.filter(date__gte=today)
        
        return queryset.order_by('date', 'departure_time')

def schedules_page(request):
    route_id = request.GET.get('route_id')
    context = {'route_id': route_id}
    return render(request, 'schedules.html', context)

def admin_check(user):
    return user.is_authenticated and user.role == 'admin'

@user_passes_test(admin_check)
def create_bus_schedule(request):
    if request.method == 'POST':
        bus_id = request.POST.get('bus')
        route_id = request.POST.get('route')
        date = request.POST.get('date')
        start_time = request.POST.get('start_time')
        end_time = request.POST.get('end_time')
        
        bus = Bus.objects.get(id=bus_id)
        route = Route.objects.get(id=route_id)
        
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

# NEW API VIEW FOR NEARBY BUSES
@api_view(['GET'])
def nearby_buses(request):
    """Get buses near user location"""
    try:
        user_lat = float(request.GET.get('latitude'))
        user_lng = float(request.GET.get('longitude'))
        radius_km = float(request.GET.get('radius', 5))
    except (TypeError, ValueError):
        return Response({
            'error': 'Invalid coordinates. Provide latitude, longitude, and optional radius.'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    # Get buses that are currently running and updated recently (last 2 hours for testing)
    two_hours_ago = timezone.now() - timedelta(hours=2)
    
    running_buses = Bus.objects.filter(
        is_running=True,
        current_latitude__isnull=False,
        current_longitude__isnull=False,
        last_location_update__gte=two_hours_ago
    ).select_related('current_route')
    
    nearby_buses_list = []
    
    for bus in running_buses:
        distance = calculate_distance(
            user_lat, user_lng,
            float(bus.current_latitude), float(bus.current_longitude)
        )
        
        if distance <= radius_km:
            bus_data = {
                'id': bus.id,
                'number_plate': bus.number_plate,
                'capacity': bus.capacity,
                'current_latitude': str(bus.current_latitude),
                'current_longitude': str(bus.current_longitude),
                'last_location_update': bus.last_location_update,
                'is_running': bus.is_running,
                'distance_km': round(distance, 2),
                'route': None,
                'schedule': None
            }
            
            # Add route info if available
            if bus.current_route:
                bus_data['route'] = {
                    'id': bus.current_route.id,
                    'number': bus.current_route.number,
                    'name': bus.current_route.name,
                    'origin': bus.current_route.origin,
                    'destination': bus.current_route.destination,
                    'total_distance': float(bus.current_route.total_distance)
                }
            
            # Find current schedule for this bus
            current_schedule = Schedule.objects.filter(
                bus=bus,
                date=timezone.now().date()
            ).first()
            
            if current_schedule:
                bus_data['schedule'] = {
                    'id': current_schedule.id,
                    'available_seats': current_schedule.available_seats,
                    'total_seats': current_schedule.total_seats,
                    'departure_time': current_schedule.departure_time.strftime('%H:%M'),
                    'arrival_time': current_schedule.arrival_time.strftime('%H:%M'),
                    'date': current_schedule.date.strftime('%Y-%m-%d')
                }
            
            nearby_buses_list.append(bus_data)
    
    nearby_buses_list.sort(key=lambda x: x['distance_km'])
    
    return Response({
        'buses': nearby_buses_list,
        'user_location': {'latitude': user_lat, 'longitude': user_lng},
        'search_radius_km': radius_km,
        'total_found': len(nearby_buses_list)
    })

def calculate_distance(lat1, lon1, lat2, lon2):
    """Calculate distance between two coordinates in kilometers"""
    R = 6371
    
    lat1_rad = math.radians(lat1)
    lon1_rad = math.radians(lon1)
    lat2_rad = math.radians(lat2)
    lon2_rad = math.radians(lon2)
    
    dlat = lat2_rad - lat1_rad
    dlon = lon2_rad - lon1_rad
    
    a = math.sin(dlat/2)**2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlon/2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    distance = R * c
    
    return distance
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def update_bus_location(request):
    """Driver endpoint to update bus location"""
    # Only drivers should access this
    if request.user.role != 'driver':
        return Response({'error': 'Only drivers can update bus locations'}, 
                       status=status.HTTP_403_FORBIDDEN)
    
    try:
        latitude = float(request.data.get('latitude'))
        longitude = float(request.data.get('longitude'))
        bus_id = request.data.get('bus_id')
        schedule_id = request.data.get('schedule_id', None)
    except (TypeError, ValueError):
        return Response({'error': 'Invalid data provided'}, 
                       status=status.HTTP_400_BAD_REQUEST)
    
    try:
        # Find the bus assigned to this driver
        bus = Bus.objects.get(id=bus_id)
        
        # Update location
        bus.update_location(latitude, longitude)
        bus.is_running = True
        
        # If schedule provided, link it
        if schedule_id:
            try:
                schedule = Schedule.objects.get(id=schedule_id, driver=request.user)
                bus.current_schedule = schedule
                bus.current_route = schedule.route
            except Schedule.DoesNotExist:
                pass
        
        bus.save()
        
        return Response({
            'success': True,
            'message': 'Location updated successfully',
            'bus': BusLocationSerializer(bus).data
        })
        
    except Bus.DoesNotExist:
        return Response({'error': 'Bus not found'}, 
                       status=status.HTTP_404_NOT_FOUND)

@api_view(['GET'])
def bus_details(request, bus_id):
    """Get detailed information about a specific bus"""
    try:
        bus = Bus.objects.select_related('current_route', 'current_schedule').get(
            id=bus_id, is_running=True
        )
        return Response(LiveBusSerializer(bus).data)
    except Bus.DoesNotExist:
        return Response({'error': 'Bus not found or not running'}, 
                       status=status.HTTP_404_NOT_FOUND)

def calculate_distance(lat1, lon1, lat2, lon2):
    """Calculate distance between two coordinates in kilometers"""
    R = 6371  # Earth's radius in kilometers
    
    lat1_rad = math.radians(lat1)
    lon1_rad = math.radians(lon1)
    lat2_rad = math.radians(lat2)
    lon2_rad = math.radians(lon2)
    
    dlat = lat2_rad - lat1_rad
    dlon = lon2_rad - lon1_rad
    
    a = math.sin(dlat/2)**2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlon/2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    distance = R * c
    
    return distance    