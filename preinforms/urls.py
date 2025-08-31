from django.urls import path
from . import views

urlpatterns = [
        path('preinform-form/', views.preinform_form_page, name='preinform-form-page'),
    path('api/preinforms/', views.PreInformCreateView.as_view(), name='preinform-create'),
]