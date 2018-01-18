from django.shortcuts import render
from django.views.decorators.http import require_http_methods
from django.shortcuts import get_object_or_404
from django.db.models import Count
from exchanges.models import Currency, ExchangePair, Exchange, ExchangeFee
from exchanges.views_helpers import get_grouped_currencies_pairs, \
    calculate_profit_base, calculate_ticker_spreads


@require_http_methods(["GET"])
def spreads(request, left="BTC", right="USD"):
    left = get_object_or_404(Currency, code=left)
    right = get_object_or_404(Currency, code=right)

    pair_groups = get_grouped_currencies_pairs()

    pairs = ExchangePair.objects.filter(left=left, right=right, active=True, exchange__active=True).order_by('exchange__id')

    profit_base = calculate_profit_base(5000, 'USD', right)
    spreads = calculate_ticker_spreads(pairs, profit_base)

    context = {
        "left": left,
        "right": right,
        "pair_groups": pair_groups,
        "spreads": spreads,
        'profit_base': profit_base
    }

    return render(request, 'exchanges/spreads.html', context)


@require_http_methods(["GET"])
def calculator(request, exchange=None, left=None, right=None):
    if exchange:
        exchange = get_object_or_404(Exchange, name=exchange, active=True)

    exchanges = Exchange.objects.annotate(pairs_count=Count('pairs')).filter(active=True, pairs_count__gt=0).all().order_by('display_name')

    if not exchange and exchanges:
        exchange = exchanges.first()

    selected_pair = None
    if exchange and left and right:
        selected_pair = get_object_or_404(ExchangePair, left__code=left, right__code=right, exchange=exchange, active=True)

    exchange_pairs = None
    if exchange:
        exchange_pairs = exchange.pairs.filter(active=True).order_by('id').all()

    if not selected_pair:
        cookie_pair = request.COOKIES.get('pair')
        if cookie_pair:
            try:
                selected_pair = ExchangePair.objects.get(id=int(cookie_pair))
            except ValueError:
                print('Deleting cookie') # todo: delete cookie

    if not selected_pair and exchange_pairs:
        selected_pair = ExchangePair.objects.filter(exchange=exchange, active=True).order_by('id').first()

    deposit_fees, withdraw_fees = None, None
    if selected_pair:
        deposit_fees = ExchangeFee.objects.filter(exchange=exchange, currency=selected_pair.right, deposit=True, active=True)
        withdraw_fees = ExchangeFee.objects.filter(exchange=exchange, currency=selected_pair.left, deposit=False, active=True)

    context = {
        "exchange": exchange,
        "exchanges": exchanges,
        "selected_pair": selected_pair,
        "exchange_pairs": exchange_pairs,
        "deposit_fees": deposit_fees,
        "withdraw_fees": withdraw_fees
    }

    return render(request, 'exchanges/calculator.html', context)