from rest_framework import generics, permissions
from .models import PreInform
from .serializers import PreInformSerializer

class PreInformCreateView(generics.CreateAPIView):
    """
    API endpoint that allows authenticated users to submit Pre-Informs.
    """
    queryset = PreInform.objects.all()
    serializer_class = PreInformSerializer
    permission_classes = [permissions.IsAuthenticated]  # Only logged-in users can submit

    def perform_create(self, serializer):
        # Automatically set the user to the currently logged-in user
        serializer.save(user=self.request.user)