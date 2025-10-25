from django.contrib import admin

from planner.models import Allergy, SubscriptionPlan, UserProfile, UserSubscription
from planner.models import Ingredient, Dish, DishIngredient

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', )


@admin.register(UserSubscription)
class UserSubscriptionAdmin(admin.ModelAdmin):
    list_display = ('user', 'plan', 'start_date', 'end_date')
    list_filter = ('plan',)
    ordering = ('end_date',)


@admin.register(SubscriptionPlan)
class SubscriptionPlanAdmin(admin.ModelAdmin):
    ordering = ('duration',)


@admin.register(Allergy)
class AllergyAdmin(admin.ModelAdmin):
    pass


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ('name', 'price', 'calories')
    list_filter = ('name',)


@admin.register(Dish)
class DishAdmin(admin.ModelAdmin):
    list_display = ('name', 'diet_type', 'category')
    list_filter = ('name', 'diet_type')


@admin.register(DishIngredient)
class DishIngredientAdmin(admin.ModelAdmin):
    list_display = ('ingredient', 'quantity')
