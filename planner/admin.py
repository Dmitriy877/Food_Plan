from django.contrib import admin

from planner.models import Allergy, SubscriptionPlan, UserProfile, UserSubscription


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', )


@admin.register(UserSubscription)
class UserSubscriptionAdmin(admin.ModelAdmin):
    list_display = ('user', 'plan', 'end_date')
    list_filter = ('plan',)
    ordering = ('end_data',)


@admin.register(SubscriptionPlan)
class SubscriptionPlanAdmin(admin.ModelAdmin):
    ordering = ('duration',)


@admin.register(Allergy)
class AllergyAdmin(admin.ModelAdmin):
    pass
