from django.test import TestCase
from exchanges.models import Exchange
from exchanges_crawler.crawlers.bitbay_crawler import BitBayCrawler


class BitBayCrawlerTestCase(TestCase):
    def setUp(self):
        Exchange.objects.create(name="BitBay")
        Exchange.objects.create(name="Cex.io")

    def test_crawler_is_properly_created(self):
        exchange = Exchange.objects.get(name="BitBay")

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
        exchange = Exchange.objects.get(name="BitBay")
        crawler = BitBayCrawler(exchange)
        left, right = 'BTC', 'USD'

        self.assertEquals(crawler.request_pair_api("", left, right), "")
        self.assertEquals(crawler.request_pair_api(None, left, right), "")

    def test_request_pair_api_raise_exception_for_invalid_url(self):
        exchange = Exchange.objects.get(name="BitBay")
        exchange.orderbook_api = 'invalid_api_url'

        crawler = BitBayCrawler(exchange)
        left, right = 'BTC', 'USD'

        with self.assertRaises(ConnectionError) as context:
            crawler.request_pair_api(exchange.orderbook_api, left, right)

        self.assertTrue('Request failed for {} ({}/{})'.format(crawler.exchange.name, left, right) in str(context.exception))

    def test_request_pair_api_returns_any_result_for_exchange_url(self):
        exchange = Exchange.objects.get(name="BitBay")
        exchange.orderbook_api = 'https://bitbay.net'

        crawler = BitBayCrawler(exchange)
        left, right = 'BTC', 'USD'

        result = crawler.request_pair_api(exchange.orderbook_api, left, right)
        self.assertTrue(result)

    def test_request_pair_api_returns_proper_result_for_orderbook_api(self):
        exchange = Exchange.objects.get(name="BitBay")
        exchange.orderbook_api = 'https://bitbay.net/API/Public/{}{}/orderbook.json'

        crawler = BitBayCrawler(exchange)
        left, right = 'BTC', 'USD'

        result = crawler.request_pair_api(exchange.orderbook_api, left, right)

        self.assertTrue('"bids":' in result)
        self.assertTrue('"asks":' in result)

    def test_request_pair_api_returns_proper_result_for_ticker_api(self):
        exchange = Exchange.objects.get(name="BitBay")
        exchange.ticker_api = 'https://bitbay.net/API/Public/{}{}/ticker.json'

        crawler = BitBayCrawler(exchange)
        left, right = 'BTC', 'USD'

        result = crawler.request_pair_api(exchange.ticker_api, left, right)

        self.assertTrue('"bid":' in result)
        self.assertTrue('"ask":' in result)

    def test_parse_pair_orderbook_returns_empty_list_for_empty_response(self):
        exchange = Exchange.objects.get(name="BitBay")
        crawler = BitBayCrawler(exchange)

        result = crawler.parse_pair_orderbook("")
        self.assertFalse(result[0])
        self.assertFalse(result[1])
        result = crawler.parse_pair_orderbook(None)
        self.assertFalse(result[0])
        self.assertFalse(result[1])

    def test_parse_pair_ticker_returns_empty_list_for_empty_response(self):
        exchange = Exchange.objects.get(name="BitBay")
        crawler = BitBayCrawler(exchange)

        result = crawler.parse_pair_ticker("")
        self.assertFalse(result[0])
        self.assertFalse(result[1])
        result = crawler.parse_pair_orderbook(None)
        self.assertFalse(result[0])
        self.assertFalse(result[1])