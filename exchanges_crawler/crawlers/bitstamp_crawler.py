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

    @staticmethod
    def fix_currency_code(code):
        return code.lower()

    async def get_orderbooks(self):
        for pair in self.exchange.pairs.all():
            if not CrawlerBase.need_update(pair):
                continue

            try:
                response = self.request_pair_api(
                    self.exchange.orderbook_api,
                    BitstampCrawler.fix_currency_code(pair.left.code),
                    BitstampCrawler.fix_currency_code(pair.right.code),
                )
            except ConnectionError:
                response = None

            if response:
                bids, asks = BitstampCrawler.parse_pair_orderbook(response)

                if BitstampCrawler.save_pair_orderbook(pair, bids, asks):
                    print(pair, 'orderbook updated')
            else:
                print(pair, 'orderbook response failed')

    async def get_tickers(self):
        for pair in self.exchange.pairs.all():
            try:
                response = self.request_pair_api(
                    self.exchange.ticker_api,
                    BitstampCrawler.fix_currency_code(pair.left.code),
                    BitstampCrawler.fix_currency_code(pair.right.code),
                )
            except ConnectionError:
                response = None

            if response:
                bid, ask = BitstampCrawler.parse_pair_ticker(response)

                if BitstampCrawler.save_pair_ticker(pair, bid, ask):
                    print(pair, 'ticker updated')
            else:
                print(pair, 'ticker response failed')


