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