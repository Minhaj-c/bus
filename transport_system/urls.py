"""
URL configuration for transport_system project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.urls import path, include 
from users.api_views import signup_view
from routes.views import api_welcome    

urlpatterns = [
    path("admin/", admin.site.urls),
    path('', include('routes.urls')),
    path('', include('schedules.urls')),
    path('', include('preinforms.urls')),
    path('', include('demand.urls')),
    path('', include('operations.urls')),
    path("api/", api_welcome, name="api-welcome"),
    path("api/signup/", signup_view, name="api-signup"),
]
"""
URL configuration for transport_system project.
"""

from django.contrib import admin
from django.urls import path, include 
from users.api_views import signup_view, login_view  # Import both functions
from routes.views import api_welcome    

urlpatterns = [
    path("admin/", admin.site.urls),
    path('', include('routes.urls')),
    path('', include('schedules.urls')),
    path('', include('preinforms.urls')),
    path('', include('demand.urls')),
    path('', include('operations.urls')),
    path("api/", api_welcome, name="api-welcome"),
    path("api/signup/", signup_view, name="api-signup"),
    path("api/login/", login_view, name="api-login"),  # Add this line
]