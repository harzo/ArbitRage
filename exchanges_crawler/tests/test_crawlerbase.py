from django.test import TestCase
from exchanges.models import Exchange
from exchanges_crawler.crawlers.crawlerbase import CrawlerBase


class CrawlerBaseTestCase(TestCase):
    def setUp(self):
        Exchange.objects.create(name="Test Exchange")

    def test_crawlerbase_is_properly_created(self):
        exchange = Exchange.objects.get(name="Test Exchange")

        base = CrawlerBase(exchange)

        self.assertEquals(exchange.id, base.exchange.id)

    def test_crawlerbase_raise_exception_for_wrong_input(self):
        with self.assertRaises(TypeError) as context:
            CrawlerBase([])

        self.assertTrue('Given argument is not Exchange type' in str(context.exception))



