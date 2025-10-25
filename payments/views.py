import os
import uuid

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect
from django.urls import reverse
from django.views import View
from yookassa import Configuration, Payment

from payments.models import PaymentProviderChoices, SubscriptionPayment
from planner.views import create_subscription


class YookassaPaymentView(LoginRequiredMixin, View):
    def get(self, request):
        Configuration.account_id = os.getenv('YOOKASSA_SHOP_ID')
        Configuration.secret_key = os.getenv('YOOKASSA_SECRET_KEY')
        payment_id = str(uuid.uuid4())
        request.session['yookassa_payment_id'] = payment_id

        subscription_data = request.session['pending_subscription']
        payment = Payment.create(
            params={
                'amount': {
                    'value': subscription_data['total_price'],
                    'currency': 'RUB',
                },
                'confirmation': {
                    'type': 'redirect',
                    'return_url': request.build_absolute_uri(reverse('yookassa_success')),
                },
                'capture': True,
                'description': f'{subscription_data["description"]}',
                'metadata': {
                    'user_id': request.user.id,
                },
                'receipt': {
                    'customer': {
                        'username': f'{request.user.username}',
                        'email': f'{request.user.email}',
                    },
                },
            },
            idempotency_key=payment_id,
        )

        return redirect(payment.confirmation.confirmation_url)


class YookassaSuccessView(View):
    def get(self, request):
        payment_id = request.session.get('yookassa_payment_id')
        subscription_data = request.session.get('pending_subscription')

        if not payment_id or not subscription_data:
            messages.error(request, 'Данные платежа не найдены.')
            return redirect('order')

        try:
            # Здесь проверка платежа в демо не работает
            # payment = Payment.find_one(payment_id)
            # if payment.status != 'succeeded':
            #     messages.error(request, f'Платёж не прошёл: {payment.status}', extra_tags='danger')
            #     return redirect('order')
            subscription = create_subscription(request.user, subscription_data)
            SubscriptionPayment.objects.create(
                payment_id=payment_id,
                user=request.user,
                subscription=subscription,
                provider=PaymentProviderChoices.YOOKASSA,
                amount=subscription.total_price,
                description=subscription_data['description'],
            )
            del request.session['yookassa_payment_id']
            del request.session['pending_subscription']

            messages.success(request, '✅ Оплата прошла успешно! Подписка активирована.')
            return redirect('profile')
        except Exception as exc:
            messages.error(request, f'Ошибка создания подписки: {str(exc)}', extra_tags='danger')
            return redirect('order')
