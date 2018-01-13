from django.test import TestCase
from exchanges.models import Exchange, Currency, ExchangePair
from exchanges_crawler.runner import init_crawlers, update_all_runner


class RunnerTestCase(TestCase):
    def test_init_crawlers_for_not_existing_class(self):
        Exchange.objects.create(name="BitBay1")
        Exchange.objects.create(name="BitBay2")
        Exchange.objects.create(name="BitBay3")

        result = init_crawlers()

        self.assertFalse(result)

    def test_init_crawlers_for_existing_class(self):
        Exchange.objects.create(name="BitBay")
        Exchange.objects.create(name="Cexio")
        Exchange.objects.create(name="Bitstamp")
        Exchange.objects.create(name="TEST")

        result = init_crawlers()

        self.assertTrue(len(result) == 3)

    def test_update_all_for_complete_data(self):
        Currency.objects.create(name="Dollar", code="USD", sign="$", sign_after=False)
        Currency.objects.create(name="Bitcoin", code="BTC", sign="BTC", crypto=True)

        Exchange.objects.create(name="BitBay",
                                orderbook_api='https://bitbay.net/API/Public/{}{}/orderbook.json',
                                ticker_api='https://bitbay.net/API/Public/{}{}/ticker.json')
        Exchange.objects.create(name="Cexio",
                                orderbook_api='https://cex.io/api/order_book/{}/{}/?depth=1',
                                ticker_api='https://cex.io/api/ticker/{}/{}')
        Exchange.objects.create(name="Bitstamp",
                                orderbook_api='https://www.bitstamp.net/api/v2/order_book/{}{}',
                                ticker_api='https://www.bitstamp.net/api/v2/ticker/{}{}')
        Exchange.objects.create(name="Kraken",
                                orderbook_api='https://api.kraken.com/0/public/Depth?pair={}{}',
                                ticker_api='https://api.kraken.com/0/public/Ticker?pair={}{}')

        exchanges = [
            #Exchange.objects.get(name="BitBay"),
            #Exchange.objects.get(name="Cexio"),
            #Exchange.objects.get(name="Kraken"),
            #Exchange.objects.get(name="Bitstamp"),
        ]

        btc = Currency.objects.get(code="BTC")
        usd = Currency.objects.get(code="USD")

        for exchange in exchanges:
            ExchangePair.objects.create(exchange=exchange, left=btc, right=usd)

        update_all_runner()

        for exchange in exchanges:
            self.assertTrue(exchange.pairs.first().bids)
            self.assertTrue(exchange.pairs.first().asks)
            self.assertTrue(exchange.pairs.first().last_bid)
            self.assertTrue(exchange.pairs.first().last_ask)


