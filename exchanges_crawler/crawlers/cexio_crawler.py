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
            try:
                response = self.request_pair_api(
                    self.exchange.orderbook_api,
                    pair.left.code,
                    pair.right.code
                )
            except ConnectionError:
                response = None

            if response:
                bids, asks = CexioCrawler.parse_pair_orderbook(response)

                if CexioCrawler.save_pair_orderbook(pair, bids, asks):
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
                bid, ask = CexioCrawler.parse_pair_ticker(response)

                if CexioCrawler.save_pair_ticker(pair, bid, ask):
                    print(pair, 'ticker updated')
            else:
                print(pair, 'ticker response failed')


