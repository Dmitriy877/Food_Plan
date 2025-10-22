from django.shortcuts import render


def index(request):
    return render(request, 'index.html')


def order(request):
    return render(request, 'order.html')

# Create your views here.
