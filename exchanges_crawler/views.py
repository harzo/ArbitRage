from django.http import HttpResponse
from exchanges_crawler.runner import update_all, update_fiats


def dev_update(request):
    update_all()

    html = "<html><body><p>Updated</p></body></html>"

    return HttpResponse(html)


def dev_fiat_update(request):
    update_fiats()

    html = "<html><body><p>Updated</p></body></html>"

    return HttpResponse(html)