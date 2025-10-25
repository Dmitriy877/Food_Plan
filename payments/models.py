from django.contrib.auth import get_user_model
from django.db import models

from planner.models import UserSubscription


class ProviderChoices(models.TextChoices):
    YOOKASSA = 'yookassa', 'ЮKassa'


class SubscriptionPayment(models.Model):
    user = models.ForeignKey(
        get_user_model(),
        on_delete=models.RESTRICT,
        related_name='payments',
    )
    subscription = models.OneToOneField(
        UserSubscription,
        on_delete=models.RESTRICT,
    )
    provider = models.CharField(
        'Платежный провайдер',
        max_length=16,
        choices=ProviderChoices.choices,
        db_index=True,
    )
    amount = models.DecimalField(
        'Сумма платежа',
        max_digits=10,
        decimal_places=2,
    )
    description = models.CharField(
        'Назначение платежа',
        max_length=100,
    )
    created_at = models.DateField(
        'Дата платежа',
        auto_now=True,
    )

    class Meta:
        verbose_name = 'Платеж за подписку'
        verbose_name_plural = 'Платежи за подписку'

    def __str__(self):
        return f"{self.user.username}: {self.description}"
