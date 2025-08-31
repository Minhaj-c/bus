from rest_framework import generics, permissions
from .models import DemandAlert
from .serializers import DemandAlertSerializer

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