from exchanges_crawler.crawlers.crawlerbase import CrawlerBase
from exchanges.models import ExchangePair
from urllib.request import Request, urlopen
import json

class BitBayCrawler(CrawlerBase):
    """
    BitBay exchange crawler.
    Exchange url: https://bitbay.net
    Orderbook scheme: {"asks": [], "bids": []}
    Ticker scheme: {"max": double, "min": double, "last": double, "bid": double,
                    "ask": double, "vwap": double, "average": double, "volume": double }
    """

    expected_name = 'BitBay'

    def __init__(self, exchange):
        super().__init__(exchange)

        if self.exchange.name != BitBayCrawler.expected_name:
            raise TypeError('Mismatched Exchange')

    def request_pair_api(self, api, left, right):
        if not api:
            return ""

        api_url = api.format(left, right)

        try:
            req = Request(api_url, None, headers={'User-Agent': 'Mozilla/5.0'})
            response = urlopen(req)
            result = str(response.read().decode(response.info().get_param('charset') or 'utf-8')).replace('\'', '"')

            return result
        except:
            raise ConnectionError('Request failed for {} ({}/{})'.format(self.exchange.name, left, right))

    def parse_pair_orderbook(self, response):
        bids = []
        asks = []

        if response:
            orderbook = json.loads(response)
            if "bids" in orderbook:
                bids = orderbook["bids"] or []
            if "asks" in orderbook:
                asks = orderbook["asks"] or []

        return bids, asks

    def parse_pair_ticker(self, response):
        last_bid = None
        last_ask = None

        if response:
            ticker = json.loads(response)
            if "bid" in ticker:
                last_bid = ticker["bid"] or []
            if "ask" in ticker:
                last_ask = ticker["ask"] or []

        return last_bid, last_ask

    def get_orderbooks(self):
        for pair in self.exchange.pairs.all():
            print(pair)