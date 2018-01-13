from exchanges_crawler.crawlers.crawlerbase import CrawlerBase
from exchanges.models import ExchangePair
import json


class CexioCrawler(CrawlerBase):
    """
    Cex.io exchange crawler.
    Exchange url: https://cex.io

    Orderbook api: https://cex.io/api/order_book/{}/{}/?depth=1
    Orderbook eg: {"timestamp":1459161809, "bids": [[250.00,0.02000000]],
                   "asks": [[280.00,20.51246433]], "pair": "BTC:USD", "id": 66478,
                   "sell_total": "707.40555590", "buy_total": "68788.80" }

    Ticker api: https://cex.io/api/ticker/{}/{}
    Ticker eg: {"timestamp": "1513011522", "low": "15250", "high": "17499",
                "last": "17099.69", "volume": "3418.33382778", "volume30d": "85621.72105143",
                "bid": 17086.43, "ask": 17092 }
    """

    expected_name = 'Cexio'

    def __init__(self, exchange):
        super().__init__(exchange)

        if self.exchange.name != CexioCrawler.expected_name:
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


