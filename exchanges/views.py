from django.shortcuts import render
from exchanges.models import Currency, ExchangePair
from django.views.decorators.http import require_http_methods
from django.shortcuts import get_object_or_404


@require_http_methods(["GET"])
def spreads(request, left="BTC", right="USD"):
    left = get_object_or_404(Currency, code=left)
    right = get_object_or_404(Currency, code=right)

    pair_groups = {}
    for obj in ExchangePair.objects.all():
        pair_groups.setdefault(obj.left.code, set()).update([obj.right.code])

    context = {
        "left": left,
        "right": right,
        "pair_groups": pair_groups
    }

    return render(request, 'exchanges/spreads.html', context)


def calculator(request):

    return render(request, 'overview/index.html')