from exchanges_crawler.crawlers.crawlerbase import CrawlerBase
from exchanges.models import ExchangePair
from urllib.request import Request, urlopen
import json


class FiatCrawler(CrawlerBase):
    """
    Fiat currencies rates crawler.
    Exchange url: https://bitbay.net

    Api: https://api.fixer.io/latest?base={}
    """

    expected_name = 'Fiat'

    def __init__(self, exchange):
        super().__init__(exchange)

        if self.exchange.name != FiatCrawler.expected_name:
            raise TypeError('Mismatched Exchange')

    @staticmethod
    def request_pair_api(api, base):
        if not api:
            return ""

        api_url = api.format(base)

        try:
            req = Request(api_url, None, headers={'User-Agent': 'Mozilla/5.0'})
            response = urlopen(req)
            result = response.read().decode(response.info().get_param('charset') or 'utf-8')

            return result
        except:
            raise ConnectionError('Api request failed!')

    @staticmethod
    def parse_pair_ticker(response, code):
        rate = None

        if response:
            ticker = json.loads(str(response).replace('\'', '"'))
            if "rates" in ticker:
                if code in ticker["rates"]:
                    rate = float(ticker["rates"][code])
        return rate

    @staticmethod
    def save_pair_ticker(pair, rate):
        if type(pair) != ExchangePair:
            return False

        if not pair.id:
            return False

        if not rate:
            return False

        pair.last_bid = rate
        pair.last_ask = rate

        pair.save()

        return True

    async def get_orderbooks(self):
        pass

    async def get_tickers(self):
        for pair in self.exchange.pairs.all():
            try:
                response = self.request_pair_api(
                    self.exchange.ticker_api,
                    pair.left.code
                )
            except ConnectionError:
                response = None

            if response:
                rate = FiatCrawler.parse_pair_ticker(response, pair.right.code)

                if FiatCrawler.save_pair_ticker(pair, rate):
                    print(pair, 'ticker updated')
            else:
                print(pair, 'ticker response failed')


