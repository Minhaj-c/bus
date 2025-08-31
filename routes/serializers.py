from rest_framework import serializers
from .models import Route, Stop

class StopSerializer(serializers.ModelSerializer):
    class Meta:
        model = Stop
        fields = ['id', 'name', 'sequence', 'distance_from_origin']

class RouteSerializer(serializers.ModelSerializer):
    # This will include the list of stops for a route in the API response
    stops = StopSerializer(many=True, read_only=True)

    class Meta:
        model = Route
        fields = ['id', 'number', 'name', 'origin', 'destination', 'total_distance', 'stops']