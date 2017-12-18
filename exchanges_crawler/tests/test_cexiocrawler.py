from django.test import TestCase
from exchanges.models import Currency, Exchange, ExchangePair
from exchanges_crawler.crawlers.cexio_crawler import CexioCrawler


class CexioCrawlerTestCase(TestCase):
    def setUp(self):
        Currency.objects.create(name="Dollar", code="USD", sign="$", sign_after=False)
        Currency.objects.create(name="Złoty", code="PLN", sign="zł")
        Currency.objects.create(name="Bitcoin", code="BTC", sign="BTC", crypto=True)

        Exchange.objects.create(name="Cexio")
        Exchange.objects.create(name="BitBay")
        self.exchange = Exchange.objects.get(name="Cexio")

        self.btc = Currency.objects.get(code="BTC")
        self.usd = Currency.objects.get(code="USD")

        ExchangePair.objects.create(exchange=self.exchange, left=self.btc, right=self.usd)

        self.orderbook_response = '{"timestamp":1459161809, "bids": [[250.00,0.02000000]], "asks": [[280.00,20.51246433]], ' \
                                  '"pair": "BTC:USD", "id": 66478, "sell_total": "707.40555590", "buy_total": "68788.80" }'

        self.ticker_response = '{"timestamp": "1513011522", "low": "15250", "high": "17499", "last": "17099.69", ' \
                               '"volume": "3418.33382778", "volume30d": "85621.72105143", "bid": 17086.43, "ask": 17092 }'

        self.saved_orderbook_bids = '[[250.0, 0.02]]'
        self.saved_orderbook_asks = '[[280.0, 20.51246433]]'
        self.saved_ticker_bid = 17086.43
        self.saved_ticker_ask = 17092

        self.orderbook_api = "https://cex.io/api/order_book/{}/{}/?depth=1"
        self.ticker_api = "https://cex.io/api/ticker/{}/{}"

    def test_crawler_is_properly_created(self):
        exchange = self.exchange

        crawler = CexioCrawler(exchange)

        self.assertEquals(exchange.id, crawler.exchange.id)

    def test_init_raise_exception_for_wrong_input(self):
        with self.assertRaises(TypeError) as context:
            CexioCrawler([])

        self.assertTrue('Given argument is not Exchange type' in str(context.exception))

    def test_init_raise_exception_for_mismatched_exchange(self):
        exchange = Exchange.objects.get(name="BitBay")

        with self.assertRaises(TypeError) as context:
            CexioCrawler(exchange)

        self.assertTrue('Mismatched Exchange' in str(context.exception))

    def test_request_pair_api_returns_empty_result_for_empty_api(self):
        left, right = 'BTC', 'USD'

        self.assertEquals(CexioCrawler.request_pair_api("", left, right), "")
        self.assertEquals(CexioCrawler.request_pair_api(None, left, right), "")

    def test_request_pair_api_raise_exception_for_invalid_url(self):
        exchange = self.exchange
        exchange.orderbook_api = 'invalid_api_url'

        left, right = 'BTC', 'USD'

        with self.assertRaises(ConnectionError) as context:
            CexioCrawler.request_pair_api(exchange.orderbook_api, left, right)

        self.assertTrue('Api request failed!' in str(context.exception))

    def test_request_pair_api_returns_any_result_for_exchange_url(self):
        exchange = self.exchange
        exchange.orderbook_api = 'https://cex.io'

        left, right = 'BTC', 'USD'

        result = CexioCrawler.request_pair_api(exchange.orderbook_api, left, right)
        self.assertTrue(result)

    def test_request_pair_api_returns_proper_result_for_orderbook_api(self):
        exchange = self.exchange
        exchange.orderbook_api = self.orderbook_api

        left, right = 'BTC', 'USD'

        result = CexioCrawler.request_pair_api(exchange.orderbook_api, left, right)

        self.assertTrue('"bids":' in result)
        self.assertTrue('"asks":' in result)

    def test_request_pair_api_returns_proper_result_for_ticker_api(self):
        exchange = self.exchange
        exchange.ticker_api = self.ticker_api

        left, right = 'BTC', 'USD'

        result = CexioCrawler.request_pair_api(exchange.ticker_api, left, right)

        self.assertTrue('"bid":' in result)
        self.assertTrue('"ask":' in result)

    def test_parse_pair_orderbook_returns_empty_lists_for_empty_response(self):

        result = CexioCrawler.parse_pair_orderbook("")
        self.assertEquals(type(result[0]), list)
        self.assertFalse(result[0])
        self.assertEquals(type(result[1]), list)
        self.assertFalse(result[1])

        result = CexioCrawler.parse_pair_orderbook(None)
        self.assertEquals(type(result[0]), list)
        self.assertFalse(result[0])
        self.assertEquals(type(result[1]), list)
        self.assertFalse(result[1])

    def test_parse_pair_orderbook_returns_parsed_data_for_mocked_response(self):
        response = self.orderbook_response

        result = CexioCrawler.parse_pair_orderbook(response)
        self.assertTrue(result[0]) # [250.00, 0.02000000]
        self.assertEquals(len(result[0]), 1)
        self.assertEquals(result[0][0][0], 250.0)
        self.assertEquals(result[0][0][1], 0.02)

        self.assertTrue(result[1]) # [280.00, 20.51246433]
        self.assertEquals(len(result[1]), 1)
        self.assertEquals(result[1][0][0], 280.00)
        self.assertEquals(result[1][0][1], 20.51246433)

    def test_parse_pair_ticker_returns_empty_list_for_empty_response(self):
        result = CexioCrawler.parse_pair_ticker("")
        self.assertIsNone(result[0])
        self.assertIsNone(result[1])

        result = CexioCrawler.parse_pair_ticker(None)
        self.assertIsNone(result[0])
        self.assertIsNone(result[1])

    def test_parse_pair_ticker_returns_parsed_data_for_mocked_response(self):
        response = self.ticker_response

        result = CexioCrawler.parse_pair_ticker(response)
        self.assertTrue(result[0]) # "bid": 17086.43
        self.assertEquals(result[0], 17086.43)

        self.assertTrue(result[1]) # "ask": 17092
        self.assertEquals(result[1], 17092)

    def test_save_pair_orderbook_for_invalid_pair(self):
        orderbook = CexioCrawler.parse_pair_orderbook(self.orderbook_response)

        result = CexioCrawler.save_pair_orderbook(None, orderbook[0], orderbook[1])

        self.assertFalse(result)

    def test_save_pair_orderbook_for_not_existing_pair(self):
        orderbook = CexioCrawler.parse_pair_orderbook(self.orderbook_response)

        exchange_pair = ExchangePair()
        result = CexioCrawler.save_pair_orderbook(exchange_pair, orderbook[0], orderbook[1])

        self.assertFalse(result)

    def test_save_pair_orderbook_for_valid_pair_and_empty_orderbook(self):
        exchange = self.exchange
        crawler = CexioCrawler(exchange)

        result = CexioCrawler.save_pair_orderbook(crawler.exchange.pairs.first(), [], [])

        self.assertFalse(result)

    def test_save_pair_orderbook_for_valid_inputs(self):
        orderbook = CexioCrawler.parse_pair_orderbook(self.orderbook_response)
        exchange = self.exchange
        crawler = CexioCrawler(exchange)
        exchange_pair = crawler.exchange.pairs.first()

        result = CexioCrawler.save_pair_orderbook(exchange_pair, orderbook[0], orderbook[1])
        self.assertTrue(result)
        self.assertEqual(exchange_pair.bids, self.saved_orderbook_bids)
        self.assertEqual(exchange_pair.asks, self.saved_orderbook_asks)

    def test_save_pair_ticker_for_invalid_pair(self):
        ticker = CexioCrawler.parse_pair_ticker(self.ticker_response)

        result = CexioCrawler.save_pair_ticker(None, ticker[0], ticker[1])

        self.assertFalse(result)

    def test_save_pair_ticker_for_not_existing_pair(self):
        ticker = CexioCrawler.parse_pair_ticker(self.ticker_response)

        exchange_pair = ExchangePair()
        result = CexioCrawler.save_pair_ticker(exchange_pair, ticker[0], ticker[1])

        self.assertFalse(result)

    def test_save_pair_ticker_for_valid_pair_and_empty_orderbook(self):
        exchange = self.exchange
        crawler = CexioCrawler(exchange)

        result = CexioCrawler.save_pair_ticker(crawler.exchange.pairs.first(), None, None)

        self.assertFalse(result)

    def test_save_pair_ticker_for_valid_inputs(self):
        ticker = CexioCrawler.parse_pair_ticker(self.ticker_response)
        exchange = self.exchange
        crawler = CexioCrawler(exchange)
        exchange_pair = crawler.exchange.pairs.first()

        result = CexioCrawler.save_pair_ticker(exchange_pair, ticker[0], ticker[1])
        self.assertTrue(result)
        self.assertEqual(exchange_pair.last_bid, self.saved_ticker_bid)
        self.assertEqual(exchange_pair.last_ask, self.saved_ticker_ask)

    # def test_get_orderbooks_change_exchange_pairs_objects(self):
    #     exchange = self.exchange
    #     exchange.orderbook_api = 'https://bitbay.net/API/Public/{}{}/orderbook.json'
    #     crawler = CexioCrawler(exchange)
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
    #     crawler = CexioCrawler(exchange)
    #
    #     crawler.get_tickers()
    #
    #     for pair in crawler.exchange.pairs.all():
    #         self.assertTrue(pair.last_bid > 0)
    #         self.assertTrue(pair.last_ask > 0)
