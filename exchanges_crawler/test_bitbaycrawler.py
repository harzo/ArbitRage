from django.test import TestCase
from exchanges.models import Currency, Exchange, ExchangePair
from exchanges_crawler.crawlers.bitbay_crawler import BitBayCrawler


class BitBayCrawlerTestCase(TestCase):
    def setUp(self):
        Currency.objects.create(name="Dollar", code="USD", sign="$", sign_after=False)
        Currency.objects.create(name="Złoty", code="PLN", sign="zł")
        Currency.objects.create(name="Bitcoin", code="BTC", sign="BTC", crypto=True)

        Exchange.objects.create(name="BitBay")
        Exchange.objects.create(name="Cex.io")
        self.exchange = Exchange.objects.get(name="BitBay")

        self.btc = Currency.objects.get(code="BTC")
        self.usd = Currency.objects.get(code="USD")

        ExchangePair.objects.create(exchange=self.exchange, left=self.btc, right=self.usd)

        self.orderbook_response = '{"bids":[[17151.01,0.055]],"asks":[[17699.99,0.01529216]]}'
        self.ticker_response = '{"max":18000,"min":16020.1,"last":17150.52,"bid":17152.01,"ask":17699.94,"vwap":17150.52,"average":17150.52,"volume":25.58984462}'

    def test_crawler_is_properly_created(self):
        exchange = self.exchange

        crawler = BitBayCrawler(exchange)

        self.assertEquals(exchange.id, crawler.exchange.id)

    def test_init_raise_exception_for_wrong_input(self):
        with self.assertRaises(TypeError) as context:
            BitBayCrawler([])

        self.assertTrue('Given argument is not Exchange type' in str(context.exception))

    def test_init_raise_exception_for_mismatched_exchange(self):
        exchange = Exchange.objects.get(name="Cex.io")

        with self.assertRaises(TypeError) as context:
            BitBayCrawler(exchange)

        self.assertTrue('Mismatched Exchange' in str(context.exception))

    def test_request_pair_api_returns_empty_result_for_empty_api(self):
        exchange = self.exchange
        crawler = BitBayCrawler(exchange)
        left, right = 'BTC', 'USD'

        self.assertEquals(crawler.request_pair_api("", left, right), "")
        self.assertEquals(crawler.request_pair_api(None, left, right), "")

    def test_request_pair_api_raise_exception_for_invalid_url(self):
        exchange = self.exchange
        exchange.orderbook_api = 'invalid_api_url'

        crawler = BitBayCrawler(exchange)
        left, right = 'BTC', 'USD'

        with self.assertRaises(ConnectionError) as context:
            crawler.request_pair_api(exchange.orderbook_api, left, right)

        self.assertTrue('Request failed for {} ({}/{})'.format(crawler.exchange.name, left, right) in str(context.exception))

    def test_request_pair_api_returns_any_result_for_exchange_url(self):
        exchange = self.exchange
        exchange.orderbook_api = 'https://bitbay.net'

        crawler = BitBayCrawler(exchange)
        left, right = 'BTC', 'USD'

        result = crawler.request_pair_api(exchange.orderbook_api, left, right)
        self.assertTrue(result)

    def test_request_pair_api_returns_proper_result_for_orderbook_api(self):
        exchange = self.exchange
        exchange.orderbook_api = 'https://bitbay.net/API/Public/{}{}/orderbook.json'

        crawler = BitBayCrawler(exchange)
        left, right = 'BTC', 'USD'

        result = crawler.request_pair_api(exchange.orderbook_api, left, right)

        self.assertTrue('"bids":' in result)
        self.assertTrue('"asks":' in result)

    def test_request_pair_api_returns_proper_result_for_ticker_api(self):
        exchange = self.exchange
        exchange.ticker_api = 'https://bitbay.net/API/Public/{}{}/ticker.json'

        crawler = BitBayCrawler(exchange)
        left, right = 'BTC', 'USD'

        result = crawler.request_pair_api(exchange.ticker_api, left, right)

        self.assertTrue('"bid":' in result)
        self.assertTrue('"ask":' in result)

    def test_parse_pair_orderbook_returns_empty_lists_for_empty_response(self):
        exchange = self.exchange
        crawler = BitBayCrawler(exchange)

        result = crawler.parse_pair_orderbook("")
        self.assertEquals(type(result[0]), list)
        self.assertFalse(result[0])
        self.assertEquals(type(result[1]), list)
        self.assertFalse(result[1])

        result = crawler.parse_pair_orderbook(None)
        self.assertEquals(type(result[0]), list)
        self.assertFalse(result[0])
        self.assertEquals(type(result[1]), list)
        self.assertFalse(result[1])

    def test_parse_pair_orderbook_returns_parsed_data_for_mocked_response(self):
        exchange = self.exchange
        crawler = BitBayCrawler(exchange)
        response = self.orderbook_response

        result = crawler.parse_pair_orderbook(response)
        self.assertTrue(result[0]) # [17151.01, 0.055]
        self.assertEquals(len(result[0]), 1)
        self.assertEquals(result[0][0][0], 17151.01)
        self.assertEquals(result[0][0][1], 0.055)

        self.assertTrue(result[1]) # [17699.99, 0.01529216]
        self.assertEquals(len(result[1]), 1)
        self.assertEquals(result[1][0][0], 17699.99)
        self.assertEquals(result[1][0][1], 0.01529216)

    def test_parse_pair_ticker_returns_empty_list_for_empty_response(self):
        exchange = self.exchange
        crawler = BitBayCrawler(exchange)

        result = crawler.parse_pair_ticker("")
        self.assertIsNone(result[0])
        self.assertIsNone(result[1])

        result = crawler.parse_pair_ticker(None)
        self.assertIsNone(result[0])
        self.assertIsNone(result[1])

    def test_parse_pair_ticker_returns_parsed_data_for_mocked_response(self):
        exchange = self.exchange
        crawler = BitBayCrawler(exchange)
        response = self.ticker_response

        result = crawler.parse_pair_ticker(response)
        self.assertTrue(result[0]) # "bid":17152.01
        self.assertEquals(result[0], 17152.01)

        self.assertTrue(result[1]) # "ask":17699.94
        self.assertEquals(result[1], 17699.94)

    def test_get_orderbooks_returns_(self):
        exchange = self.exchange
        crawler = BitBayCrawler(exchange)
        # response = self.orderbook_response

        crawler.get_orderbooks()
