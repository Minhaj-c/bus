from rest_framework import serializers
from .models import DemandAlert

class DemandAlertSerializer(serializers.ModelSerializer):
    class Meta:
        model = DemandAlert
        fields = ['id', 'user', 'stop', 'number_of_people', 'status', 'created_at', 'expires_at']
        read_only_fields = ['id', 'user', 'status', 'created_at', 'expires_at']  # These are set by the system