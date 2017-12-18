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
    def parse_pair_orderbook(response):
        bids = []
        asks = []

        if response:
            orderbook = json.loads(str(response).replace('\'', '"'))
            if "bids" in orderbook:
                bids = orderbook["bids"]
            if "asks" in orderbook:
                asks = orderbook["asks"]

        return bids, asks

    @staticmethod
    def parse_pair_ticker(response):
        last_bid = None
        last_ask = None

        if response:
            ticker = json.loads(response)
            if "bid" in ticker:
                last_bid = ticker["bid"]
            if "ask" in ticker:
                last_ask = ticker["ask"]

        return last_bid, last_ask

    @staticmethod
    def save_pair_orderbook(pair, bids, asks):
        if type(pair) != ExchangePair:
            return False

        if not pair.id:
            return False

        if not bids and not asks:
            return False

        if type(bids) == list:
            pair.bids = json.dumps(bids)

        if type(asks) == list:
            pair.asks = json.dumps(asks)

        pair.save()

        return True

    @staticmethod
    def save_pair_ticker(pair, bid, ask):
        if type(pair) != ExchangePair:
            return False

        if not pair.id:
            return False

        if not bid and not ask:
            return False

        if bid > 0:
            pair.last_bid = bid

        if ask > 0:
            pair.last_ask = ask

        pair.save()

        return True

    def get_orderbooks(self):
        for pair in self.exchange.pairs.all():
            try:
                response = self.request_pair_api(
                    self.exchange.orderbook_api,
                    pair.left.code,
                    pair.right.code
                )
            except ConnectionError:
                response = None

            if response:
                bids, asks = BitBayCrawler.parse_pair_orderbook(response)

                if BitBayCrawler.save_pair_orderbook(pair, bids, asks):
                    print(pair, 'orderbook updated')
            else:
                print(pair, 'orderbook response failed')

    def get_tickers(self):
        for pair in self.exchange.pairs.all():
            try:
                response = self.request_pair_api(
                    self.exchange.ticker_api,
                    pair.left.code,
                    pair.right.code
                )
            except ConnectionError:
                response = None

            if response:
                bid, ask = BitBayCrawler.parse_pair_ticker(response)

                if BitBayCrawler.save_pair_ticker(pair, bid, ask):
                    print(pair, 'ticker updated')
            else:
                print(pair, 'ticker response failed')


