from django.http import HttpResponse
from exchanges_crawler.runner import update_all_runner, update_fiats_runner


def dev_update(request):
    update_all_runner()

    html = "<html><body><p>Updated</p></body></html>"

    return HttpResponse(html)


def dev_fiat_update(request):
    update_fiats_runner()

    html = "<html><body><p>Updated</p></body></html>"

    return HttpResponse(html)