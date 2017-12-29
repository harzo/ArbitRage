from django.shortcuts import render
from exchanges.models import Currency, ExchangePair
from django.views.decorators.http import require_http_methods
from django.shortcuts import get_object_or_404
import json


@require_http_methods(["GET"])
def spreads(request, left="BTC", right="USD"):
    left = get_object_or_404(Currency, code=left)
    right = get_object_or_404(Currency, code=right)

    pair_groups = get_grouped_currencies_pairs()

    pairs = ExchangePair.objects.filter(left=left, right=right).all().order_by('exchange__id')
    spreads = calculate_ticker_spreads(pairs)

    context = {
        "left": left,
        "right": right,
        "pair_groups": pair_groups,
        "spreads": spreads
    }

    return render(request, 'exchanges/spreads.html', context)


def get_grouped_currencies_pairs():
    pair_groups = {}
    for obj in ExchangePair.objects.all():
        pair_groups.setdefault(obj.left.code, set()).update([obj.right.code])

    return pair_groups


def calculate_ticker_spreads(pairs):
    spreads = []

    for pair_idx in range(len(pairs)):
        for pair_idx2 in range(len(pairs)):
            if pair_idx == pair_idx2:
                continue

            spread = pairs[pair_idx2].last_ask - pairs[pair_idx].last_bid

            if spread > 0:
                spreads.append({
                    'buy_exchange': pairs[pair_idx].exchange,
                    'sell_exchange': pairs[pair_idx2].exchange,
                    'spread': spread
                })

    spreads.sort(key=lambda x: -x['spread'])

    return spreads


def calculate_orderbook_buy_value(pair, right_amount):
    bids = json.load(pair.bids)

    amount_left = right_amount
    value = 0

    for bid in bids:
        bid_amount = bid[0]*bid[1]

        if bid_amount >= amount_left:
            ratio = amount_left/bid_amount

            amount_left = 0
            value += bid[1]*ratio
        else:
            amount_left -= bid_amount
            value += bid[1]

    return value


def calculate_orderbook_sell_amount(pair, left_value):
    asks = json.load(pair.asks)

    value_left = left_value
    amount = 0

    for ask in asks:
        ask_value = ask[1]

        if ask_value >= value_left:
            ratio = value_left/ask_value

            value_left = 0
            amount += ask[0]*ask[1]*ratio
        else:
            value_left -= ask_value
            amount += ask[0]*ask[1]

    return amount


def calculator(request):

    return render(request, 'overview/index.html')