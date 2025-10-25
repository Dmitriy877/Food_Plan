from django.contrib import admin

from payments.models import SubscriptionPayment


@admin.register(SubscriptionPayment)
class SubscriptionPaymentAdmin(admin.ModelAdmin):
    list_display = ('payment_id', 'user', 'provider', 'amount', 'created_at')
    list_filter = ('provider',)
