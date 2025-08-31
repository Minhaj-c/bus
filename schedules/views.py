from rest_framework import generics
from django.utils import timezone
from .models import Schedule
from .serializers import ScheduleSerializer

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