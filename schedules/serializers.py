from rest_framework import serializers
from .models import Schedule, Bus
from routes.serializers import RouteSerializer  # We'll use this to nest route info

class BusSerializer(serializers.ModelSerializer):
    class Meta:
        model = Bus
        fields = ['id', 'number_plate', 'capacity']

class ScheduleSerializer(serializers.ModelSerializer):
    # Nest the related bus and route information in the API response
    bus = BusSerializer(read_only=True)
    route = RouteSerializer(read_only=True)
    
    class Meta:
        model = Schedule
        fields = ['id', 'route', 'bus', 'date', 'departure_time', 'arrival_time', 'total_seats', 'available_seats']
        
class BusLocationSerializer(serializers.ModelSerializer):
    """Serializer for bus location data"""
    class Meta:
        model = Bus
        fields = [
            'id', 'number_plate', 'current_latitude', 'current_longitude',
            'last_location_update', 'is_running', 'current_route', 'current_schedule'
        ]

class LiveBusSerializer(serializers.ModelSerializer):
    """Serializer for live bus tracking"""
    route = RouteSerializer(source='current_route', read_only=True)
    schedule = serializers.SerializerMethodField()
    
    class Meta:
        model = Bus
        fields = [
            'id', 'number_plate', 'capacity', 'current_latitude', 
            'current_longitude', 'last_location_update', 'is_running',
            'route', 'schedule'
        ]
    
    def get_schedule(self, obj):
        if obj.current_schedule:
            return {
                'id': obj.current_schedule.id,
                'available_seats': obj.current_schedule.available_seats,
                'total_seats': obj.current_schedule.total_seats,
                'departure_time': obj.current_schedule.departure_time,
                'arrival_time': obj.current_schedule.arrival_time,
                'date': obj.current_schedule.date
            }
        return None

class ScheduleSerializer(serializers.ModelSerializer):
    # This might already exist, but ensure it includes bus details
    route = RouteSerializer(read_only=True)
    bus = BusLocationSerializer(read_only=True)
    driver = serializers.SerializerMethodField()

    class Meta:
        model = Schedule
        fields = [
            'id', 'route', 'bus', 'driver', 'date', 'departure_time', 
            'arrival_time', 'total_seats', 'available_seats'
        ]

    def get_driver(self, obj):
        return {
            'id': obj.driver.id,
            'name': f"{obj.driver.first_name} {obj.driver.last_name}".strip() or obj.driver.email
        }
        