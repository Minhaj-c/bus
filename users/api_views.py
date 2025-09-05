from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.contrib.auth import get_user_model
from django.db import IntegrityError
from django.views.decorators.csrf import csrf_exempt
import json
from django.contrib.auth import authenticate, login
from django.views.decorators.csrf import ensure_csrf_cookie
from django.middleware.csrf import get_token
from django.contrib.sessions.models import Session

User = get_user_model()

@api_view(['POST'])
def signup_view(request):
    try:
        data = request.data
        email = data.get('email')
        password = data.get('password')
        first_name = data.get('first_name')
        last_name = data.get('last_name')
        role = data.get('role', 'passenger')
        
        # Validate required fields
        if not email or not password:
            return Response({'error': 'Email and password are required'}, 
                            status=status.HTTP_400_BAD_REQUEST)
        
        # Check if user already exists
        if User.objects.filter(email=email).exists():
            return Response({'error': 'User with this email already exists'}, 
                          status=status.HTTP_400_BAD_REQUEST)
        
        # Create new user
        user = User.objects.create_user(
            email=email,
            password=password,
            first_name=first_name or '',
            last_name=last_name or '',
            role=role
        )
        
        return Response({
            'success': True,
            'user': {
                'id': user.id,
                'email': user.email,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'role': user.role
            }
        }, status=status.HTTP_201_CREATED)
        
    except IntegrityError:
        return Response({'error': 'User with this email already exists'}, 
                      status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return Response({'error': f'An error occurred: {str(e)}'}, 
                      status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
def login_view(request):
    try:
        data = request.data
        email = data.get('email')
        password = data.get('password')
        
        if not email or not password:
            return Response({'error': 'Email and password required'}, 
                          status=status.HTTP_400_BAD_REQUEST)
        
        user = authenticate(request, email=email, password=password)
        if user is not None:
            login(request, user)  # This sets request.user
            
            # Force session save
            request.session.save()
            
            return Response({
                'success': True,
                'user': {
                    'id': user.id,
                    'email': user.email,
                    'first_name': user.first_name,
                    'last_name': user.last_name,
                    'role': user.role
                },
                'session_key': request.session.session_key  # Add this for debugging
            }, status=status.HTTP_200_OK)
        else:
            return Response({'error': 'Invalid credentials'}, 
                          status=status.HTTP_401_UNAUTHORIZED)
            
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)