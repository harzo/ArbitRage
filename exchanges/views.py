from django.shortcuts import render
from exchanges.models import Currency


def spreads(request):

    currencies = Currency.objects.all()

    context = {
        "currencies": currencies
    }

    return render(request, 'exchanges/spreads.html', context)


def calculator(request):

    return render(request, 'overview/index.html')