from django.shortcuts import redirect
from django.views.generic import CreateView

from .forms import CustomUserCreationForm


class CustomRegisterView(CreateView):
    template_name = 'auth/registration.html'
    form_class = CustomUserCreationForm
    success_url = '/'

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('index')
        return super().dispatch(request, *args, **kwargs)
