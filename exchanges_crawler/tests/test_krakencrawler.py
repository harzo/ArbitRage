from django.test import TestCase
from exchanges.models import Currency, Exchange, ExchangePair
from exchanges_crawler.crawlers.kraken_crawler import KrakenCrawler


class KrakenCrawlerTestCase(TestCase):
    def setUp(self):
        self.url = 'https://www.kraken.com'

        Currency.objects.create(name="Dollar", code="USD", sign="$", sign_after=False)
        Currency.objects.create(name="Złoty", code="PLN", sign="zł")
        Currency.objects.create(name="Bitcoin", code="BTC", sign="BTC", crypto=True)

        Exchange.objects.create(name="Kraken")
        Exchange.objects.create(name="Cex.io")
        self.exchange = Exchange.objects.get(name="Kraken")

        self.btc = Currency.objects.get(code="BTC")
        self.usd = Currency.objects.get(code="USD")

        ExchangePair.objects.create(exchange=self.exchange, left=self.btc, right=self.usd)

        self.orderbook_response = '{"error": [], "result": {"XXBTZUSD": {"bids":[["17151.01","0.055", 1513689432]],' \
                                  '"asks":[["17699.99","0.01529216", 1513689432]]}}}'
        self.ticker_response = '{"error": [], "result": {"XXBTZUSD": {"a": ["17699.94000", "1", "1.000"], ' \
                               '"b": ["17152.01000", "2", "2.000"],' \
                               ' "c": ["18286.50000", "0.00314585"], "v": ["2251.57215593", "3533.43568912"], ' \
                               '"p": ["18499.30405", "18556.15103"], "t": [15947, 27773],' \
                               '"l": ["17712.90000", "17712.90000"], "h": ["18946.80000", "19000.00000"], "o": "18832.80000"}}}'

        self.saved_orderbook_bids = '[[17151.01, 0.055]]'
        self.saved_orderbook_asks = '[[17699.99, 0.01529216]]'
        self.saved_ticker_bid = 17152.01
        self.saved_ticker_ask = 17699.94

        self.orderbook_api = "https://api.kraken.com/0/public/Depth?pair={}{}"
        self.ticker_api = "https://api.kraken.com/0/public/Ticker?pair={}{}"

    def test_crawler_is_properly_created(self):
        exchange = self.exchange

        crawler = KrakenCrawler(exchange)

        self.assertEquals(exchange.id, crawler.exchange.id)

    def test_init_raise_exception_for_wrong_input(self):
        with self.assertRaises(TypeError) as context:
            KrakenCrawler([])

        self.assertTrue('Given argument is not Exchange type' in str(context.exception))

    def test_init_raise_exception_for_mismatched_exchange(self):
        exchange = Exchange.objects.get(name="Cex.io")

        with self.assertRaises(TypeError) as context:
            KrakenCrawler(exchange)

        self.assertTrue('Mismatched Exchange' in str(context.exception))

    def test_request_pair_api_returns_empty_result_for_empty_api(self):
        left, right = 'XBT', 'USD'

        self.assertEquals(KrakenCrawler.request_pair_api("", left, right), "")
        self.assertEquals(KrakenCrawler.request_pair_api(None, left, right), "")

    def test_request_pair_api_raise_exception_for_invalid_url(self):
        exchange = self.exchange
        exchange.orderbook_api = 'invalid_api_url'

        left, right = 'XBT', 'USD'

        with self.assertRaises(ConnectionError) as context:
            KrakenCrawler.request_pair_api(exchange.orderbook_api, left, right)

        self.assertTrue('Api request failed!' in str(context.exception))

    def test_request_pair_api_returns_any_result_for_exchange_url(self):
        exchange = self.exchange
        exchange.orderbook_api = self.url

        left, right = 'XBT', 'USD'

        result = KrakenCrawler.request_pair_api(exchange.orderbook_api, left, right)
        self.assertTrue(result)

    def test_request_pair_api_returns_proper_result_for_orderbook_api(self):
        exchange = self.exchange
        exchange.orderbook_api = self.orderbook_api

        left, right = 'XBT', 'USD'

        result = KrakenCrawler.request_pair_api(exchange.orderbook_api, left, right)

        self.assertTrue('"bids":' in result)
        self.assertTrue('"asks":' in result)

    def test_request_pair_api_returns_proper_result_for_ticker_api(self):
        exchange = self.exchange
        exchange.ticker_api = self.ticker_api

        left, right = 'XBT', 'USD'

        result = KrakenCrawler.request_pair_api(exchange.ticker_api, left, right)

        self.assertTrue('"b":' in result)
        self.assertTrue('"a":' in result)

    def test_parse_pair_orderbook_returns_empty_lists_for_empty_response(self):

        result = KrakenCrawler.parse_pair_orderbook("")
        self.assertEquals(type(result[0]), list)
        self.assertFalse(result[0])
        self.assertEquals(type(result[1]), list)
        self.assertFalse(result[1])

        result = KrakenCrawler.parse_pair_orderbook(None)
        self.assertEquals(type(result[0]), list)
        self.assertFalse(result[0])
        self.assertEquals(type(result[1]), list)
        self.assertFalse(result[1])

    def test_parse_pair_orderbook_returns_parsed_data_for_mocked_response(self):
        response = self.orderbook_response

        result = KrakenCrawler.parse_pair_orderbook(response)
        self.assertTrue(result[0]) # [17151.01, 0.055]
        self.assertEquals(len(result[0]), 1)
        self.assertEquals(result[0][0][0], 17151.01)
        self.assertEquals(result[0][0][1], 0.055)

        self.assertTrue(result[1]) # [17699.99, 0.01529216]
        self.assertEquals(len(result[1]), 1)
        self.assertEquals(result[1][0][0], 17699.99)
        self.assertEquals(result[1][0][1], 0.01529216)

    def test_parse_pair_ticker_returns_empty_list_for_empty_response(self):
        result = KrakenCrawler.parse_pair_ticker("")
        self.assertIsNone(result[0])
        self.assertIsNone(result[1])

        result = KrakenCrawler.parse_pair_ticker(None)
        self.assertIsNone(result[0])
        self.assertIsNone(result[1])

    def test_parse_pair_ticker_returns_parsed_data_for_mocked_response(self):
        response = self.ticker_response

        result = KrakenCrawler.parse_pair_ticker(response)
        self.assertTrue(result[0]) # "bid":17152.01
        self.assertEquals(result[0], 17152.01)

        self.assertTrue(result[1]) # "ask":17699.94
        self.assertEquals(result[1], 17699.94)

    def test_save_pair_orderbook_for_invalid_pair(self):
        orderbook = KrakenCrawler.parse_pair_orderbook(self.orderbook_response)

        result = KrakenCrawler.save_pair_orderbook(None, orderbook[0], orderbook[1])

        self.assertFalse(result)

    def test_save_pair_orderbook_for_not_existing_pair(self):
        orderbook = KrakenCrawler.parse_pair_orderbook(self.orderbook_response)

        exchange_pair = ExchangePair()
        result = KrakenCrawler.save_pair_orderbook(exchange_pair, orderbook[0], orderbook[1])

        self.assertFalse(result)

    def test_save_pair_orderbook_for_valid_pair_and_empty_orderbook(self):
        exchange = self.exchange
        crawler = KrakenCrawler(exchange)

        result = KrakenCrawler.save_pair_orderbook(crawler.exchange.pairs.first(), [], [])

        self.assertFalse(result)

    def test_save_pair_orderbook_for_valid_inputs(self):
        orderbook = KrakenCrawler.parse_pair_orderbook(self.orderbook_response)
        exchange = self.exchange
        crawler = KrakenCrawler(exchange)
        exchange_pair = crawler.exchange.pairs.first()

        result = KrakenCrawler.save_pair_orderbook(exchange_pair, orderbook[0], orderbook[1])
        self.assertTrue(result)
        self.assertEqual(exchange_pair.bids, self.saved_orderbook_bids)
        self.assertEqual(exchange_pair.asks, self.saved_orderbook_asks)

    def test_save_pair_ticker_for_invalid_pair(self):
        ticker = KrakenCrawler.parse_pair_ticker(self.ticker_response)

        result = KrakenCrawler.save_pair_ticker(None, ticker[0], ticker[1])

        self.assertFalse(result)

    def test_save_pair_ticker_for_not_existing_pair(self):
        ticker = KrakenCrawler.parse_pair_ticker(self.ticker_response)

        exchange_pair = ExchangePair()
        result = KrakenCrawler.save_pair_ticker(exchange_pair, ticker[0], ticker[1])

        self.assertFalse(result)

    def test_save_pair_ticker_for_valid_pair_and_empty_orderbook(self):
        exchange = self.exchange
        crawler = KrakenCrawler(exchange)

        result = KrakenCrawler.save_pair_ticker(crawler.exchange.pairs.first(), None, None)

        self.assertFalse(result)

    def test_save_pair_ticker_for_valid_inputs(self):
        ticker = KrakenCrawler.parse_pair_ticker(self.ticker_response)
        exchange = self.exchange
        crawler = KrakenCrawler(exchange)
        exchange_pair = crawler.exchange.pairs.first()

        result = KrakenCrawler.save_pair_ticker(exchange_pair, ticker[0], ticker[1])
        self.assertTrue(result)
        self.assertEqual(exchange_pair.last_bid, self.saved_ticker_bid)
        self.assertEqual(exchange_pair.last_ask, self.saved_ticker_ask)

    # def test_get_orderbooks_change_exchange_pairs_objects(self):
    #     exchange = self.exchange
    #     exchange.orderbook_api = 'https://bitbay.net/API/Public/{}{}/orderbook.json'
    #     crawler = KrakenCrawler(exchange)
    #
    #     crawler.get_orderbooks()
    #
    #     for pair in crawler.exchange.pairs.all():
    #         self.assertTrue(pair.bids)
    #         self.assertTrue(pair.asks)
    #
    # def test_get_tickers_change_exchange_pairs_objects(self):
    #     exchange = self.exchange
    #     exchange.ticker_api = 'https://bitbay.net/API/Public/{}{}/ticker.json'
    #     crawler = KrakenCrawler(exchange)
    #
    #     crawler.get_tickers()
    #
    #     for pair in crawler.exchange.pairs.all():
    #         self.assertTrue(pair.last_bid > 0)
    #         self.assertTrue(pair.last_ask > 0)
