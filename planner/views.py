import json
from typing import Any

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import ValidationError
from django.http import JsonResponse
from django.shortcuts import render
from django.urls import reverse
from django.views import View
from django.views.generic import FormView

from planner.forms import SubscriptionForm
from planner.models import MealTypeChoices, SubscriptionPlan


def card(request):
    return render(request, 'card1.html')


@login_required
def lk(request):
    return render(request, 'lk.html')


class OrderView(LoginRequiredMixin, FormView):
    template_name = 'order.html'
    form_class = SubscriptionForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['meal_types'] = MealTypeChoices
        plan = SubscriptionPlan.objects.get(duration=1)
        context['total_price'] = plan.total_price(MealTypeChoices)

        return context

    def form_valid(self, form):
        # TODO: валидацию на наличие оплаченной подписки, оплату и создание подписки
        raise ValidationError('Ошибка валидации')
        self.success_url = reverse('lk')
        messages.success(self.request, 'Подписка успешно создана!')
        return super().form_valid(form)


def _validate_subscription_data(subs_data: dict[str, Any]) -> tuple[int, int, list]:
    term = int(subs_data.get('term', 0))
    if not term or term not in {choice[0] for choice in SubscriptionPlan.DURATION_CHOICES}:
        raise ValidationError('Неизвестная продолжительность подписки.')
    persons_count = int(subs_data.get('persons', 1))
    if persons_count not in {choice[0] for choice in SubscriptionForm.PERSONS_CHOICES}:
        raise ValidationError('Неверное количество персон.')
    selected_meals = [
        meal_type for meal_type in MealTypeChoices
        if subs_data.get(str(meal_type.value)) == 'True'
    ]
    if not selected_meals:
        raise ValidationError('Должен быть выбран хотя бы один приём пищи.')
    return term, persons_count, selected_meals


class CalculateSubscription(View):
    def post(self, request):
        try:
            subs_data = json.loads(request.body)
            term, persons_count, selected_meals = _validate_subscription_data(subs_data)
            plan = SubscriptionPlan.objects.get(duration=term)
            total_price = plan.total_price(selected_meals) * persons_count
            return JsonResponse({'totalPrice': total_price}, status=200)
        except json.JSONDecodeError as error:
            return JsonResponse({'error': str(error)}, status=400)
        except ValidationError as error:
            return JsonResponse({'error': str(error)}, status=400)
        except Exception:
            return JsonResponse({'error': 'unexpected server error'}, status=500)
