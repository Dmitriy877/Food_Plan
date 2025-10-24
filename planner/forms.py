from django import forms
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
