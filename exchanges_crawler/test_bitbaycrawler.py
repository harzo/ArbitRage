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

    def test_crawler_raise_exception_for_wrong_input(self):
        with self.assertRaises(TypeError) as context:
            BitBayCrawler([])

        self.assertTrue('Given argument is not Exchange type' in str(context.exception))

    def test_crawler_raise_exception_for_mismatched_exchange(self):
        exchange = Exchange.objects.get(name="Cex.io")

        with self.assertRaises(TypeError) as context:
            BitBayCrawler(exchange)

        self.assertTrue('Mismatched Exchange' in str(context.exception))

