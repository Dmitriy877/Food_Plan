from django.contrib import admin

from planner.models import SubscriptionPlan, UserProfile, Allergy


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'diet_type', 'plan', 'subscription_end_date')
    list_filter = ('plan', 'diet_type')
    ordering = ('subscription_end_date',)


@admin.register(SubscriptionPlan)
class SubscriptionPlanAdmin(admin.ModelAdmin):
    ordering = ('duration',)

@admin.register(Allergy)
class AllergyAdmin(admin.ModelAdmin):
    pass
