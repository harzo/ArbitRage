from exchanges.models import Exchange, ExchangePair
from urllib.request import Request, urlopen
from exchanges_crawler.models import ExchangePairSettings
from django.utils import timezone
import datetime
import json


class CrawlerBase:

    def __init__(self, exchange):
        if exchange.__class__ != Exchange:
            raise TypeError('Given argument is not Exchange type')

        self.exchange = exchange
        self.code_mapping = None

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
    def validate_pair(pair):
        if type(pair) != ExchangePair:
            return False

        if not pair.id:
            return False

        return True

    @staticmethod
    def clear_pair_orderbook(pair):
        if not CrawlerBase.validate_pair(pair):
            return

        pair.bids = None
        pair.asks = None

        pair.save()

    @staticmethod
    def clear_pair_ticker(pair):
        if not CrawlerBase.validate_pair(pair):
            return

        pair.last_bid = 0.0
        pair.last_ask = 0.0

        pair.save()

    @staticmethod
    def need_update(pair):
        pair_settings = ExchangePairSettings.objects.filter(left=pair.left, right=pair.right).first()
        update_frequency = 30

        if not pair_settings:
            ExchangePairSettings.objects.create(left=pair.left, right=pair.right)
        else:
            update_frequency = pair_settings.update_frequency

        need = timezone.now() - datetime.timedelta(minutes=update_frequency) >= pair.updated

        if need:
            CrawlerBase.clear_pair_orderbook(pair)

        return need

    def save_pair_orderbook(self, pair, bids, asks):
        if not CrawlerBase.validate_pair(pair):
            return False

        if not bids and not asks:
            return False

        if type(bids) == list:
            pair.bids = json.dumps(bids)

        if type(asks) == list:
            pair.asks = json.dumps(asks)

        pair.save()

        return True

    def save_pair_ticker(self, pair, bid, ask):
        if not CrawlerBase.validate_pair(pair):
            return False

        if not bid and not ask:
            return False

        if bid > 0:
            pair.last_bid = bid

        if ask > 0:
            pair.last_ask = ask

        pair.save()

        return True

    async def get_orderbooks(self):
        for pair in self.exchange.pairs.all():
            if not CrawlerBase.need_update(pair):
                continue

            try:
                response = self.request_pair_api(
                    self.exchange.orderbook_api,
                    self.fix_currency_code(pair.left.code),
                    self.fix_currency_code(pair.right.code)
                )
            except ConnectionError:
                response = None

            if response:
                bids, asks = self.parse_pair_orderbook(response)

                if self.save_pair_orderbook(pair, bids, asks):
                    print(pair, 'orderbook updated')
            else:
                print(pair, 'orderbook response failed')

    async def get_tickers(self):
        for pair in self.exchange.pairs.all():
            CrawlerBase.clear_pair_ticker(pair)

            try:
                response = self.request_pair_api(
                    self.exchange.ticker_api,
                    self.fix_currency_code(pair.left.code),
                    self.fix_currency_code(pair.right.code)
                )
            except ConnectionError:
                response = None

            if response:
                bid, ask = self.parse_pair_ticker(response)

                if self.save_pair_ticker(pair, bid, ask):
                    print(pair, 'ticker updated')
            else:
                print(pair, 'ticker response failed')

    # todo: install package for abstracts/interfaces
    # interface
    def parse_pair_orderbook(self, response):
        return response

    # interface
    def parse_pair_ticker(self, response):
        return response

    # interface
    def fix_currency_code(self, code):
        return code
