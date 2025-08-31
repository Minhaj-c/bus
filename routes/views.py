from django.http import JsonResponse
from rest_framework import generics
from .models import Route
from .serializers import RouteSerializer
from django.shortcuts import render 

# Add this new function at the top of the file
def api_welcome(request):
    """A simple welcome message for the API root"""
    return JsonResponse({
        'message': 'Welcome to the Transport Management API!',
        'endpoints': {
            'routes': '/api/routes/',
            'admin': '/admin/',
            'schedules': '/api/schedules/?route_id=1&date=2023-10-27',
            'preinforms': '/api/preinforms/',
        }
    })
    
def homepage(request):
    """Serve the main frontend page"""
    return render(request, 'homepage.html')
    

class RouteListView(generics.ListAPIView):
    """API view to list all bus routes."""
    queryset = Route.objects.all().prefetch_related('stops')
    serializer_class = RouteSerializer