from django.http import HttpResponse
from exchanges_crawler.runner import update_all


def dev_update(request):
    update_all()

    html = "<html><body><p>Updated</p></body></html>"

    return HttpResponse(html)
