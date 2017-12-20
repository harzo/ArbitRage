from django.shortcuts import render
from exchanges.models import Currency
from django.views.decorators.http import require_http_methods
from django.shortcuts import get_object_or_404


@require_http_methods(["GET"])
def spreads(request, left="BTC", right="USD"):
    get_object_or_404(Currency, code=left)
    get_object_or_404(Currency, code=right)

    currencies = Currency.objects.all()

    context = {
        "currencies": currencies
    }

    return render(request, 'exchanges/spreads.html', context)


def calculator(request):

    return render(request, 'overview/index.html')