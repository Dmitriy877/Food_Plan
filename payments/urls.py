from django.urls import path

from . import views

urlpatterns = [
    path('yookassa/', views.YookassaPaymentView.as_view(), name='yookassa_payment'),
    path('yookassa/success/', views.YookassaPaymentView.as_view(), name='yookassa_success'),
]
