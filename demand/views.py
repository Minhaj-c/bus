from rest_framework import generics, permissions
from .models import DemandAlert
from .serializers import DemandAlertSerializer
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from routes.models import Stop

class DemandAlertCreateView(generics.CreateAPIView):
    """
    API endpoint for registered users to report demand at a stop.
    """
    queryset = DemandAlert.objects.all()
    serializer_class = DemandAlertSerializer
    permission_classes = [permissions.IsAuthenticated]  # Must be logged in

    def perform_create(self, serializer):
        # Automatically set the user to the currently logged-in user
        serializer.save(user=self.request.user)
        
@login_required
def demand_alert_page(request):
    """Serve the demand alert form page"""
    # Get all stops for the dropdown
    stops = Stop.objects.all().order_by('name')
    context = {'stops': stops}
    return render(request, 'demand_alert.html', context)        