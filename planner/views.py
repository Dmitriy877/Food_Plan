import json
from typing import Any

from dateutil.relativedelta import relativedelta
from django.contrib import messages
from django.contrib.auth import get_user_model, update_session_auth_hash
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import ValidationError
from django.http import JsonResponse
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.utils import timezone
from django.views import View
from django.views.generic import DetailView, FormView

from planner.forms import SubscriptionForm, UserProfileForm
from planner.models import DailyMenu, Dish, MealTypeChoices, SubscriptionPlan, UserProfile, UserSubscription

User = get_user_model()


def _validate_subscription_data(subs_data: dict[str, Any]) -> tuple[int, int, list]:
    try:
        term = int(subs_data.get('term', 0))
        persons_count = int(subs_data.get('persons', 1))
    except (TypeError, ValueError):
        raise ValidationError('Неверный формат данных')
    if not term or term not in {choice[0] for choice in SubscriptionPlan.DURATION_CHOICES}:
        raise ValidationError('Неизвестная продолжительность подписки.')
    if persons_count not in {choice[0] for choice in SubscriptionForm.PERSONS_CHOICES}:
        raise ValidationError('Неверное количество персон.')
    selected_meals = [
        meal_type for meal_type in MealTypeChoices
        if subs_data.get(str(meal_type.value)) in {'True', True}
    ]
    if not selected_meals:
        raise ValidationError('Должен быть выбран хотя бы один приём пищи.')
    return term, persons_count, selected_meals


def create_subscription(
    user: User,
    subscription_data: dict[str, Any],
) -> UserSubscription:
    term, persons_count, selected_meals = _validate_subscription_data(subscription_data)
    subscription = UserSubscription.objects.create(
        user=user,
        diet_type=subscription_data['foodtype'],
        selected_meal_types=selected_meals,
        persons_count=persons_count,
        plan=SubscriptionPlan.objects.get(duration=term),
        end_date=timezone.now().date() + relativedelta(months=term),
    )
    subscription.allergies.set(subscription_data['allergies'])
    subscription.save()
    return subscription


class OrderView(FormView):
    template_name = 'order.html'
    form_class = SubscriptionForm
    success_url = reverse_lazy('profile')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['meal_types'] = MealTypeChoices
        plan = SubscriptionPlan.objects.get(duration=1)
        context['total_price'] = plan.total_price(MealTypeChoices)

        return context

    def form_valid(self, form):
        if not self.request.user.is_authenticated:
            messages.warning(
                self.request, 'Для оформления подписки необходимо войти в систему.',
            )
            return redirect('login')

        if UserSubscription.objects.filter(user=self.request.user).exists():
            messages.warning(self.request, 'У Вас уже есть оплаченная подписка.')
            return redirect('profile')

        cleaned_data = form.cleaned_data.copy()
        term = cleaned_data['term']
        if 'allergies' in cleaned_data:
            cleaned_data['allergies'] = [allergy.id for allergy in cleaned_data['allergies']]
        cleaned_data['description'] = f'Подписка FoodPlan на {SubscriptionPlan.get_duration_display_by_value(term)}'
        self.request.session['pending_subscription'] = cleaned_data
        return redirect('yookassa_payment')


class CalculateSubscription(View):
    def post(self, request):
        try:
            subs_data = json.loads(request.body)
            term, persons_count, selected_meals = _validate_subscription_data(subs_data)
            plan = SubscriptionPlan.objects.get(duration=term)
            total_price = plan.total_price(selected_meals) * persons_count
            return JsonResponse({'totalPrice': total_price}, status=200)
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Неверный формат JSON'}, status=400)
        except ValidationError as error:
            return JsonResponse({'error': str(error)}, status=400)
        except SubscriptionPlan.DoesNotExist:
            return JsonResponse({'error': 'Выбранный план подписки не найден'}, status=400)
        except Exception:
            return JsonResponse({'error': 'Внутренняя ошибка сервера'}, status=500)


class ProfileView(LoginRequiredMixin, FormView):
    template_name = 'profile.html'
    form_class = UserProfileForm
    success_url = reverse_lazy('profile')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user

        menu_data = DailyMenu.get_todays_menu_with_dishes(user)
        if menu_data:
            context['daily_menu'] = menu_data['menu']
            context['daily_meals'] = menu_data['meals']

        context['meal_types'] = MealTypeChoices.choices

        return context

    def form_valid(self, form):
        try:
            original_username = self.request.user.username
            form.save()
            is_password_changed = bool(form.cleaned_data.get('new_password1'))
            is_username_changed = form.cleaned_data.get('username') != original_username
            if is_password_changed:
                update_session_auth_hash(self.request, self.request.user)
                messages.success(self.request, 'Пароль успешно изменён.')
            if is_username_changed:
                messages.success(self.request, 'Имя пользователя успешно изменено.')

            return super().form_valid(form)
        except Exception as exc:
            messages.error(self.request, f'Ошибка сохранения: {str(exc)}', extra_tags='danger')
            return self.form_invalid(form)


class UploadAvatarView(LoginRequiredMixin, View):
    def post(self, request):
        avatar = request.FILES.get('avatar')
        if not avatar:
            return JsonResponse({'success': False, 'error': 'No file provided.'})
        try:
            profile = UserProfile.objects.get(user=request.user)
            profile.avatar = avatar
            profile.save()
            return JsonResponse({'success': True, 'avatar_url': profile.avatar.url})
        except Exception as exc:
            return JsonResponse({'success': False, 'error': str(exc)}, status=400)


class RegenerateMenuView(LoginRequiredMixin, View):
    def post(self, request):
        daily_menu = DailyMenu.generate_for_user(request.user)
        if daily_menu:
            messages.success(request, 'Меню успешно обновлено!')

        return redirect('profile')


class DishDetailView(LoginRequiredMixin, DetailView):
    model = Dish
    template_name = 'dish_detail.html'
    context_object_name = 'dish'

    def get_queryset(self):
        if hasattr(self.request.user, 'subscription'):
            return Dish.objects.get_dishes_for_subscription(self.request.user.subscription)
        return Dish.objects.none()
