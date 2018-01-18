from exchanges.models import ExchangePair, Currency


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
    buy_value = calculate_buy_volume(buy_pair, amount)

    sell_amount = calculate_sell_amount(sell_pair, buy_value)

    return sell_amount - amount


def calculate_buy_volume(pair, right_amount, taker=True):
    try:
        asks = eval(pair.asks)
    except:
        return 0

    volume = calculate_volume(asks, right_amount)

    return volume*(1-(pair.exchange.taker_fee if taker else pair.exchange.maker_fee))


def calculate_buy_amount(pair, left_volume, taker=True):
    try:
        asks = eval(pair.asks)
    except:
        return 0

    left_volume = left_volume/(1-(pair.exchange.taker_fee if taker else pair.exchange.maker_fee))

    return calculate_amount(asks, left_volume)


def calculate_sell_amount(pair, left_volume, taker=True):
    try:
        bids = eval(pair.bids)
    except:
        return 0

    amount = calculate_amount(bids, left_volume)

    return amount*(1-(pair.exchange.taker_fee if taker else pair.exchange.maker_fee))


def calculate_volume(orderbook, amount):
    amount_left = amount
    volume = 0

    for order in orderbook:
        o_rate, o_volume = float(order[0]), float(order[1])
        order_amount = o_rate * o_volume

        if order_amount >= amount_left:
            ratio = amount_left/order_amount

            amount_left = 0
            volume += o_volume*ratio
        else:
            amount_left -= order_amount
            volume += o_volume
            
    return volume


def calculate_amount(orderbook, volume):
    volume_left = volume
    amount = 0

    for order in orderbook:
        o_rate, o_volume = float(order[0]), float(order[1])

        order_volume = o_volume

        if order_volume >= volume_left:
            ratio = volume_left/order_volume

            volume_left = 0
            amount += o_rate*o_volume*ratio
        else:
            volume_left -= order_volume
            amount += o_rate*o_volume

    return amount