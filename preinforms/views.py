from rest_framework import generics, permissions
from .models import PreInform
from .serializers import PreInformSerializer
from django.contrib.auth.decorators import login_required
from schedules.models import Schedule
from django.shortcuts import render

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

@login_required  # Ensure only logged-in users can access this page
def preinform_form_page(request):
    """Serve the pre-inform form page"""
    schedule_id = request.GET.get('schedule_id')
    try:
        schedule = Schedule.objects.get(id=schedule_id)
        context = {'schedule': schedule}
        return render(request, 'preinform_form.html', context)
    except Schedule.DoesNotExist:
        return render(request, 'error.html', {'message': 'Schedule not found'})        