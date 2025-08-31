from rest_framework import serializers
from .models import PreInform
from routes.models import Stop  # We need this for validation

class PreInformSerializer(serializers.ModelSerializer):
    class Meta:
        model = PreInform
        fields = ['id', 'route', 'date_of_travel', 'desired_time', 'boarding_stop', 'passenger_count', 'status', 'created_at']
        read_only_fields = ['id', 'status', 'created_at']  # These are set by the system, not the user

    def validate(self, data):
        """
        Custom validation to ensure the boarding stop belongs to the selected route.
        """
        route = data.get('route')
        boarding_stop = data.get('boarding_stop')
        
        if boarding_stop not in route.stops.all():
            raise serializers.ValidationError("The selected boarding stop does not belong to this route.")
        
        return data