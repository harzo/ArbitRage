from exchanges_crawler.crawlers.crawlerbase import CrawlerBase
from exchanges.models import ExchangePair
import json


class BitstampCrawler(CrawlerBase):
    """
    Bitstamp exchange crawler.
    Exchange url: https://www.bitstamp.net/

    Orderbook api: https://www.bitstamp.net/api/v2/order_book/{}{}
    Orderbook eg: {"timestamp":1459161809, "bids": [[250.00,0.02000000]], "asks": [[280.00,20.51246433]] }

    Ticker api: https://www.bitstamp.net/api/v2/ticker/{}{}
    Ticker eg: {"high": "19310.67", "last": "18708.60", "timestamp": "1513614037", "bid": "18690.00",
                "vwap": "18723.62", "volume": "15137.32985455", "low": "17835.20", "ask": "18710.65",
                "open": "18953.00"}
    """

    expected_name = 'Bitstamp'

    def __init__(self, exchange):
        super().__init__(exchange)

        if self.exchange.name != BitstampCrawler.expected_name:
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
            ticker = json.loads(response)
            if "bid" in ticker:
                last_bid = float(ticker["bid"])
            if "ask" in ticker:
                last_ask = float(ticker["ask"])

        return last_bid, last_ask

    def fix_currency_code(self, code):
        return code.lower()



