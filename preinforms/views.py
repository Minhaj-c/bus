from rest_framework import generics, permissions
from .models import PreInform
from .serializers import PreInformSerializer
from django.contrib.auth.decorators import login_required
from schedules.models import Schedule
from django.shortcuts import render
from django.contrib.auth import get_user_model

User = get_user_model()

class PreInformCreateView(generics.CreateAPIView):
    """
    API endpoint that allows users to submit Pre-Informs.
    """
    queryset = PreInform.objects.all()
    serializer_class = PreInformSerializer
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
def preinform_form_page(request):
    """Serve the pre-inform form page"""
    schedule_id = request.GET.get('schedule_id')
    try:
        schedule = Schedule.objects.get(id=schedule_id)
        context = {'schedule': schedule}
        return render(request, 'preinform_form.html', context)
    except Schedule.DoesNotExist:
        return render(request, 'error.html', {'message': 'Schedule not found'})