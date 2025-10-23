from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.views.generic import TemplateView

from planner.models import MealType


def index(request):
    return render(request, 'index.html')


def order(request):
    return render(request, 'order.html')


def card(request):
    return render(request, 'card1.html')


@login_required
def lk(request):
    return render(request, 'lk.html')

class SubscriptionView(TemplateView):
    template_name = 'order.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['meal_types'] = MealType.objects.all()
