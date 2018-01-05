from exchanges_crawler.crawlers.crawlerbase import CrawlerBase
from exchanges.models import ExchangePair
import json


class BitBayCrawler(CrawlerBase):
    """
    BitBay exchange crawler.
    Exchange url: https://bitbay.net

    Orderbook api: https://bitbay.net/API/Public/{}{}/orderbook.json
    Orderbook eg: {"bids":[[1519.00,0.07],[1513.00,0.13]], "asks":[[1529.00,0.09],[1531.00,0.12]]}

    Ticker api: https://bitbay.net/API/Public/{}{}/ticker.json
    Ticker eg: {"max":4500,"min":1465,"last":1533,"bid":1513,"ask":1542,"vwap":1524.42,
                "average":1545.67,"volume":4.54042857}
    """

    expected_name = 'BitBay'

    def __init__(self, exchange):
        super().__init__(exchange)

        if self.exchange.name != BitBayCrawler.expected_name:
            raise TypeError('Mismatched Exchange')

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
            ticker = json.loads(str(response).replace('\'', '"'))
            if "bid" in ticker:
                last_bid = float(ticker["bid"])
            if "ask" in ticker:
                last_ask = float(ticker["ask"])

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

    async def get_orderbooks(self):
        for pair in self.exchange.pairs.all():
            if not CrawlerBase.need_update(pair):
                continue

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

    async def get_tickers(self):
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