from exchanges_crawler.crawlers.crawlerbase import CrawlerBase
from exchanges.models import ExchangePair
import json


class KrakenCrawler(CrawlerBase):
    """
    Kraken exchange crawler.
    Exchange url: https://www.kraken.com

    Orderbook api: https://api.kraken.com/0/public/Depth?pair={}{}
    Orderbook eg: {"error":[],"result":{"X{}Z{}":{"bids": [["18295.00000","0.011",1513689432]],
                   "asks": [["18328.30000","0.006",1513689450]]}}}

    Ticker api: https://api.kraken.com/0/public/Ticker?pair={}{}
    Ticker eg: {"error":[],"result":{"X{}Z{}":{"a":["18286.50000","1","1.000"],"b":["18225.10000","2","2.000"],
                "c":["18286.50000","0.00314585"],"v":["2251.57215593","3533.43568912"],
                "p":["18499.30405","18556.15103"],"t":[15947,27773],"l":["17712.90000","17712.90000"],
                "h":["18946.80000","19000.00000"],"o":"18832.80000"}}}
    """

    expected_name = 'Kraken'
    code_mapping = {
        'BTC': 'XBT',
        'XBT': 'BTC'
    }

    def __init__(self, exchange):
        super().__init__(exchange)

        if self.exchange.name != KrakenCrawler.expected_name:
            raise TypeError('Mismatched Exchange')

    @staticmethod
    def parse_pair_orderbook(response):
        bids = []
        asks = []

        if response:
            orderbook = json.loads(str(response).replace('\'', '"'))
            if "result" in orderbook:
                orderbook = orderbook["result"]

            if orderbook:
                orderbook = orderbook[list(orderbook.keys())[0]]

            if "bids" in orderbook:
                bids = [[float(bid[0]), float(bid[1])] for bid in orderbook["bids"]]
            if "asks" in orderbook:
                asks = [[float(ask[0]), float(ask[1])] for ask in orderbook["asks"]]

        return bids, asks

    @staticmethod
    def parse_pair_ticker(response):
        last_bid = None
        last_ask = None

        if response:
            ticker = json.loads(str(response).replace('\'', '"'))
            if "result" in ticker:
                ticker = ticker["result"]

            if ticker:
                ticker = ticker[list(ticker.keys())[0]]

            if "b" in ticker:
                last_bid = float(ticker["b"][0])
            if "a" in ticker:
                last_ask = float(ticker["a"][0])

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
        if code in KrakenCrawler.code_mapping:
            return KrakenCrawler.code_mapping[code]
        else:
            return code

    async def get_orderbooks(self):
        for pair in self.exchange.pairs.all():
            try:
                response = self.request_pair_api(
                    self.exchange.orderbook_api,
                    KrakenCrawler.fix_currency_code(pair.left.code),
                    KrakenCrawler.fix_currency_code(pair.right.code)
                )
            except ConnectionError:
                response = None

            if response:
                bids, asks = KrakenCrawler.parse_pair_orderbook(response)

                if KrakenCrawler.save_pair_orderbook(pair, bids, asks):
                    print(pair, 'orderbook updated')
            else:
                print(pair, 'orderbook response failed')

    async def get_tickers(self):
        for pair in self.exchange.pairs.all():
            try:
                response = self.request_pair_api(
                    self.exchange.ticker_api,
                    KrakenCrawler.fix_currency_code(pair.left.code),
                    KrakenCrawler.fix_currency_code(pair.right.code)
                )
            except ConnectionError:
                response = None

            if response:
                bid, ask = KrakenCrawler.parse_pair_ticker(response)

                if KrakenCrawler.save_pair_ticker(pair, bid, ask):
                    print(pair, 'ticker updated')
            else:
                print(pair, 'ticker response failed')


