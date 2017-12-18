from django.test import TestCase
from exchanges.models import Exchange, Currency, ExchangePair
from exchanges_crawler.runner import init_crawlers, update_all


class RunnerTestCase(TestCase):
    def test_init_crawlers_for_not_existing_class(self):
        Exchange.objects.create(name="BitBay1")
        Exchange.objects.create(name="BitBay2")
        Exchange.objects.create(name="BitBay3")

        result = init_crawlers()

        self.assertFalse(result)

    def test_init_crawlers_for_existing_class(self):
        Exchange.objects.create(name="BitBay")
        Exchange.objects.create(name="BitBay")

        result = init_crawlers()

        self.assertTrue(len(result) == 2)

    def test_update_all_for_complete_data(self):
        Currency.objects.create(name="Dollar", code="USD", sign="$", sign_after=False)
        Currency.objects.create(name="Bitcoin", code="BTC", sign="BTC", crypto=True)

        Exchange.objects.create(name="BitBay",
                                orderbook_api = 'https://bitbay.net/API/Public/{}{}/orderbook.json',
                                ticker_api='https://bitbay.net/API/Public/{}{}/ticker.json')

        exchange = Exchange.objects.get(name="BitBay")
        btc = Currency.objects.get(code="BTC")
        usd = Currency.objects.get(code="USD")

        ExchangePair.objects.create(exchange=exchange, left=btc, right=usd)


        update_all()

        self.assertTrue(exchange.pairs.first().bids)
        self.assertTrue(exchange.pairs.first().asks)
        self.assertTrue(exchange.pairs.first().last_bid)
        self.assertTrue(exchange.pairs.first().last_ask)
        print(exchange.pairs.first().last_bid)
        print(exchange.pairs.first().last_ask)


