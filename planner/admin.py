from django.contrib import admin

from planner.models import (
    Allergy, Dish, DishIngredient, Ingredient, SubscriptionPlan,
    UserProfile, UserSubscription, DailyMenu, DailyMeal
)


class DailyMealInline(admin.TabularInline):
    model = DailyMeal
    extra = 1
    fields = ('meal_type', 'dish')


@admin.register(DailyMenu)
class DailyMenuAdmin(admin.ModelAdmin):
    list_display = ('user', 'date', 'meals_count', 'total_calories')
    list_filter = ('date', 'user')
    search_fields = ('user__username',)
    readonly_fields = ('total_calories', 'total_cooking_time')
    inlines = [DailyMealInline]

    def meals_count(self, obj):
        return obj.meals.count()
    meals_count.short_description = 'Приемов пищи'


@admin.register(DailyMeal)
class DailyMealAdmin(admin.ModelAdmin):
    list_display = ('daily_menu', 'meal_type', 'dish')
    list_filter = ('meal_type', 'daily_menu__date')
    search_fields = ('daily_menu__user__username', 'dish__name')


class DishIngredientInline(admin.TabularInline):
    model = DishIngredient
    extra = 1
    fields = ('ingredient', 'quantity', 'total_calories')
    readonly_fields = ('total_calories',)


@admin.register(Dish)
class DishAdmin(admin.ModelAdmin):
    list_display = ('name', 'diet_type', 'category', 'cooking_time', 'difficulty', 'total_calories',
                    'calories_per_portion')
    list_filter = ('diet_type', 'category', 'difficulty')
    search_fields = ('name', 'description')
    readonly_fields = ('total_calories', 'calories_per_portion', 'is_vegetarian')
    fieldsets = (
        ('Основная информация', {
            'fields': ('name', 'description', 'photo', 'diet_type', 'category'),
        }),
        ('Приготовление', {
            'fields': ('recipe', 'cooking_time', 'difficulty', 'portions'),
        }),
        ('Расчеты', {
            'fields': ('total_calories', 'calories_per_portion', 'is_vegetarian'),
            'classes': ('collapse',),
        }),
    )
    inlines = [DishIngredientInline]


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ('name', 'calories', 'unit', 'allergens_list')
    list_filter = ('unit', 'allergens')
    search_fields = ('name',)
    filter_horizontal = ('allergens',)

    def allergens_list(self, obj):
        return ", ".join([allergy.name for allergy in obj.allergens.all()])

    allergens_list.short_description = 'Аллергены'


@admin.register(DishIngredient)
class DishIngredientAdmin(admin.ModelAdmin):
    list_display = ('dish', 'ingredient', 'quantity', 'unit_display', 'total_calories')
    list_filter = ('dish__diet_type', 'dish__category', 'ingredient__allergens')
    search_fields = ('dish__name', 'ingredient__name')

    def unit_display(self, obj):
        return obj.ingredient.get_unit_display()

    unit_display.short_description = 'Единица измерения'

    def total_calories(self, obj):
        return obj.total_calories

    total_calories.short_description = 'Калории'


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user',)


@admin.register(UserSubscription)
class UserSubscriptionAdmin(admin.ModelAdmin):
    list_display = ('user', 'diet_type', 'plan', 'persons_count', 'start_date', 'end_date', 'is_active')
    list_filter = ('plan', 'diet_type', 'start_date')
    ordering = ('end_date',)
    filter_horizontal = ('allergies',)

    def is_active(self, obj):
        return obj.is_active

    is_active.boolean = True
    is_active.short_description = 'Активна'


@admin.register(SubscriptionPlan)
class SubscriptionPlanAdmin(admin.ModelAdmin):
    list_display = ('duration', 'breakfast_price', 'lunch_price', 'dinner_price', 'dessert_price')
    ordering = ('duration',)


@admin.register(Allergy)
class AllergyAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)