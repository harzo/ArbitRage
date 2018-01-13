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

    def parse_pair_orderbook(self, response):
        bids = []
        asks = []

        if response:
            orderbook = json.loads(str(response).replace('\'', '"'))
            if "bids" in orderbook:
                bids = orderbook["bids"]
            if "asks" in orderbook:
                asks = orderbook["asks"]

        return bids, asks

    def parse_pair_ticker(self, response):
        last_bid = None
        last_ask = None

        if response:
            ticker = json.loads(str(response).replace('\'', '"'))
            if "bid" in ticker:
                last_bid = float(ticker["bid"])
            if "ask" in ticker:
                last_ask = float(ticker["ask"])

        return last_bid, last_ask
