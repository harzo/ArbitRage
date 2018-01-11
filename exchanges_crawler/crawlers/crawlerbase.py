from exchanges.models import Exchange
from urllib.request import Request, urlopen
from exchanges_crawler.models import ExchangePairSettings
from django.utils import timezone
import datetime


class CrawlerBase:

    def __init__(self, exchange):
        if exchange.__class__ != Exchange:
            raise TypeError('Given argument is not Exchange type')

        self.exchange = exchange

    @staticmethod
    def request_pair_api(api, left, right):
        if not api:
            return ""

        api_url = api.format(left, right)

        try:
            req = Request(api_url, None, headers={'User-Agent': 'Mozilla/5.0'})
            response = urlopen(req)
            result = response.read().decode(response.info().get_param('charset') or 'utf-8')

            return result
        except:
            raise ConnectionError('Api request failed!')

    @staticmethod
    def need_update(pair):
        pair_settings = ExchangePairSettings.objects.filter(left=pair.left, right=pair.right).first()
        update_frequency = 30

        if not pair_settings:
            ExchangePairSettings.objects.create(left=pair.left, right=pair.right)
        else:
            update_frequency = pair_settings.update_frequency

        need = timezone.now() - datetime.timedelta(minutes=update_frequency) >= pair.updated

        return need