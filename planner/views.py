from django.contrib.auth.decorators import login_required
from django.shortcuts import render


def index(request):
    return render(request, 'index.html')


def order(request):
    return render(request, 'order.html')


def card(request):
    return render(request, 'card1.html')


@login_required
def lk(request):
    return render(request, 'lk.html')
