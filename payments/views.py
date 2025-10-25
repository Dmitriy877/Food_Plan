import os
import uuid

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect
from django.urls import reverse
from django.views import View
from yookassa import Configuration, Payment

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


class YookassaSuccessView(LoginRequiredMixin, View):
    def get(self, request):
        payment_id = request.session.get('yookassa_payment_id')
        subscription_data = request.session.get('pending_subscription')

        if not payment_id or not subscription_data:
            messages.error(request, 'Данные платежа не найдены.')
            return redirect('order')

        try:
            create_subscription(request.user, subscription_data)
            del request.session['yookassa_payment_id']
            del request.session['pending_subscription']
        except Exception as exc:
            messages.error(request, f'Ошибка создания подписки: {str(exc)}')
            return redirect('order')
