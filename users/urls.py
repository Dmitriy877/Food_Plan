from django.contrib.auth.views import LoginView, LogoutView
from django.urls import path
from django.views.generic import CreateView

from .forms import CustomUserCreationForm

urlpatterns = [
    path(
        'register/',
        CreateView.as_view(
            template_name='registration.html',
            form_class=CustomUserCreationForm,
            success_url='/',
        ),
        name='register'),
    path(
        'login/',
        LoginView.as_view(
            template_name='auth.html'
        ),
        name='login'
    ),
    path(
        'logout/',
        LogoutView.as_view(
            template_name='index.html'
        ),
        name='logout'
    ),
]
