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

    pairs = ExchangePair.objects.filter(left=left, right=right, active=True).all().order_by('exchange__id')

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


def get_grouped_currencies_pairs():
    pair_groups = {}
    for obj in ExchangePair.objects.filter(active=True).all():
        pair_groups.setdefault(obj.left.code, set()).update([obj.right.code])

    return pair_groups


def calculate_ticker_spreads(pairs, profit_base):
    spreads = []

    for pair_idx in range(len(pairs)):
        for pair_idx2 in range(len(pairs)):
            if pair_idx == pair_idx2:
                continue

            spread = pairs[pair_idx2].last_bid - pairs[pair_idx].last_ask

            if spread > 0:
                profit = calculate_basic_profit(profit_base, pairs[pair_idx], pairs[pair_idx2])

                if profit > 0:
                    spreads.append({
                        'buy_exchange': pairs[pair_idx].exchange,
                        'sell_exchange': pairs[pair_idx2].exchange,
                        'buy_rate': pairs[pair_idx].last_ask,
                        'sell_rate': pairs[pair_idx2].last_bid,
                        'spread': spread,
                        'profit': profit
                    })

    spreads.sort(key=lambda x: -x['profit'])

    return spreads


def calculate_profit_base(amount, code, right):
    if code == right.code:
        return amount

    left = Currency.objects.filter(code=code).first()

    if not left:
        return 0

    pair = ExchangePair.objects.filter(left=right, right=left).first()

    if not pair:
        return 0

    return amount/pair.last_ask


def calculate_basic_profit(amount, buy_pair, sell_pair):
    buy_value = calculate_orderbook_buy_value(buy_pair, amount)

    sell_amount = calculate_orderbook_sell_amount(sell_pair, buy_value)

    return sell_amount - amount


def calculate_orderbook_buy_value(pair, right_amount):
    asks = eval(pair.asks)

    amount_left = right_amount
    value = 0

    for ask in asks:
        b_rate, b_value = float(ask[0]), float(ask[1])
        ask_amount = b_rate * b_value

        if ask_amount >= amount_left:
            ratio = amount_left/ask_amount

            amount_left = 0
            value += b_value*ratio
        else:
            amount_left -= ask_amount
            value += b_value

    return value*(1-pair.exchange.taker_fee)


def calculate_orderbook_sell_amount(pair, left_value):
    bids = eval(pair.bids)

    value_left = left_value
    amount = 0

    for bid in bids:
        a_rate, a_value = float(bid[0]), float(bid[1])

        bid_value = a_value

        if bid_value >= value_left:
            ratio = value_left/bid_value

            value_left = 0
            amount += a_rate*a_value*ratio
        else:
            value_left -= bid_value
            amount += a_rate*a_value

    return amount


def calculator(request):

    return render(request, 'overview/index.html')