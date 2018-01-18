from django.views.decorators.http import require_POST
from django.http import JsonResponse
from exchanges.models import ExchangePair
from exchanges.views_helpers import calculate_buy_amount, calculate_buy_volume


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


def response_bad_request(message):
    return JsonResponse({'status': 'false', 'message': message}, status=400)