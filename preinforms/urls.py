from django.urls import path
from . import views

urlpatterns = [
    path('api/preinforms/', views.PreInformCreateView.as_view(), name='preinform-create'),
]