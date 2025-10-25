from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.utils.safestring import mark_safe

from planner.models import Allergy, DietTypeChoices, MealTypeChoices, SubscriptionPlan


class SubscriptionForm(forms.Form):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for meal_type in MealTypeChoices:
            self.fields[str(meal_type.value)] = forms.BooleanField(
                initial=True,
                label=str(meal_type.label),
                widget=forms.Select(
                    choices=[(True, mark_safe('&#10004;')), (False, mark_safe('&#10008;'))],
                    attrs={'class': 'form-select'}),
                required=False,
            )

    PERSONS_CHOICES = [(count, str(count)) for count in range(1, 7)]

    foodtype = forms.ChoiceField(
        choices=DietTypeChoices,
        widget=forms.RadioSelect(attrs={
            'class': 'foodplan_selected d-none',
            'form': 'order',
        }),
        initial=DietTypeChoices.CLASSIC.value,
        required=True,
    )
    term = forms.ChoiceField(
        choices=SubscriptionPlan.DURATION_CHOICES,
        initial=1,
        widget=forms.Select(attrs={
            'class': 'form-select',
        }),
        required=True,
    )
    persons = forms.ChoiceField(
        choices=PERSONS_CHOICES,
        initial=1,
        widget=forms.Select(attrs={
            'class': 'form-select',
        }),
        required=True,
    )
    allergies = forms.ModelMultipleChoiceField(
        queryset=Allergy.objects.all(),
        widget=forms.CheckboxSelectMultiple(attrs={
            'class': 'form-check-input me-1 foodplan_checked-green',
        }),
        required=False,
    )

    def clean(self):
        cleaned_data = self.cleaned_data
        term = int(cleaned_data.get('term', 0))
        persons_count = int(cleaned_data.get('persons', 1))
        if not term or term not in {choice[0] for choice in SubscriptionPlan.DURATION_CHOICES}:
            raise ValidationError({'term': 'Неизвестная продолжительность подписки.'})
        if persons_count not in {choice[0] for choice in SubscriptionForm.PERSONS_CHOICES}:
            raise ValidationError({'persons': 'Неверное количество персон.'})
        selected_meals = [
            meal_type for meal_type in MealTypeChoices
            if cleaned_data.get(str(meal_type.value)) is True
        ]
        if not selected_meals:
            raise ValidationError('Должен быть выбран хотя бы один приём пищи.')
        plan = SubscriptionPlan.objects.get(duration=term)
        cleaned_data['total_price'] = float(plan.total_price(selected_meals) * persons_count)
        cleaned_data['term'] = term
        cleaned_data['persons'] = persons_count
        return cleaned_data


class UserProfileForm(forms.Form):
    username = forms.CharField(
        max_length=50,
        widget=forms.TextInput(
            attrs={'class': 'form-control', 'readonly': True},
        ),
        required=False,
    )
    new_password1 = forms.CharField(
        max_length=100,
        widget=forms.PasswordInput(
            attrs={'class': 'form-control', 'readonly': True},
        ),
        required=False,
    )
    new_password2 = forms.CharField(
        max_length=100,
        widget=forms.PasswordInput(
            attrs={'class': 'form-control', 'readonly': True},
        ),
        required=False,
    )

    def __init__(self, user, *args, **kwargs):
        self.user = user
        super().__init__(*args, **kwargs)
        self.fields['username'].initial = self.user.username

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if username and username != self.user.username:
            if get_user_model().objects.filter(username=username).exclude(pk=self.user.pk).exists():
                raise ValidationError('Пользователь с таким именем уже существует.')
        return username

    def clean(self):
        cleaned_data = super().clean()
        password1 = cleaned_data.get('new_password1')
        password2 = cleaned_data.get('new_password2')
        if password1 or password2:
            if password1 != password2:
                raise ValidationError({'new_password2': 'Пароли не совпадают.'})
            try:
                validate_password(password2, self.user)
            except ValidationError as error:
                raise ValidationError({'new_password1': error.messages})

        return cleaned_data

    def save(self):
        username = self.cleaned_data.get('username')
        password = self.cleaned_data.get('new_password1')
        if username and username != self.user.username:
            self.user.username = username
            self.user.save()
        if password:
            self.user.set_password(password)
            self.user.save()

        return self.user
