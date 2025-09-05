from rest_framework import generics, permissions
from .models import DemandAlert
from .serializers import DemandAlertSerializer
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from routes.models import Stop
from django.contrib.auth import get_user_model

User = get_user_model()

class DemandAlertCreateView(generics.CreateAPIView):
    """
    API endpoint for users to report demand at a stop.
    """
    queryset = DemandAlert.objects.all()
    serializer_class = DemandAlertSerializer
    permission_classes = [permissions.AllowAny]  # CHANGED: Allow anyone for testing

    def perform_create(self, serializer):
        # Use authenticated user if available, otherwise use first user for testing
        if self.request.user.is_authenticated:
            serializer.save(user=self.request.user)
        else:
            # For testing - get any user from database
            test_user = User.objects.first()
            if test_user:
                serializer.save(user=test_user)
            else:
                # If no users exist, create a test user
                test_user = User.objects.create_user(
                    email='test@example.com',
                    password='testpass',
                    role='passenger'
                )
                serializer.save(user=test_user)
        
@login_required
def demand_alert_page(request):
    """Serve the demand alert form page"""
    stops = Stop.objects.all().order_by('name')
    context = {'stops': stops}
    return render(request, 'demand_alert.html', context)