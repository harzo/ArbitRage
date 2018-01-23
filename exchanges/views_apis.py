from django.views.decorators.http import require_POST
from django.http import JsonResponse
from exchanges.models import ExchangePair
from exchanges.views_helpers import calculate_buy_amount, calculate_buy_volume, calculate_sell_amount


@require_POST
def calculate_buy_amount_volume(request):
    try:
        value = eval(request.POST.get('value'))
    except:
        return response_bad_request("Corrupted data (value)")

    try:
        pair_id = request.POST.get('pair_id')
        pair = ExchangePair.objects.get(id=eval(pair_id))
    except:
        return response_bad_request("Corrupted data (pair_id)")

    side = request.POST.get('side')

    if side not in ['left', 'right']:
        return response_bad_request("Corrupted data (side)")

    result = calculate_buy_amount(pair, value) if side == 'left' else calculate_buy_volume(pair, value)

    response = {
        'status': 'true',
        'result': result
    }

    return JsonResponse(response)


@require_POST
def calculate_sell_results(request):
    try:
        volume = eval(request.POST.get('volume'))
    except:
        return response_bad_request("Corrupted data (volume)")

    try:
        amount = eval(request.POST.get('amount'))
    except:
        return response_bad_request("Corrupted data (amount)")

    try:
        pair_id = request.POST.get('pair_id')
        pair = ExchangePair.objects.get(id=eval(pair_id))
    except:
        return response_bad_request("Corrupted data (pair_id)")

    pairs = ExchangePair.objects.filter(left=pair.left, right=pair.right, active=True, exchange__active=True).exclude(id=pair.id)

    # todo: concurrency
    sell_amounts = []
    for pair in pairs:
        sell_amount = calculate_sell_amount(pair, volume)
        if amount < sell_amount:
            sell_amounts.append({
                'exchange_name': pair.exchange.display_name,
                'exchange_id': pair.exchange.id,
                'amount': sell_amount,
                'rate': sell_amount/volume,
                'profit': sell_amount-amount,
                'percent': (sell_amount-amount)/amount
            })

    response = {
        'sell_amounts': sell_amounts
    }

    return JsonResponse(response)


def response_bad_request(message):
    return JsonResponse({'status': 'false', 'message': message}, status=400)