from exchanges_crawler.crawlers.crawlerbase import CrawlerBase


class BitBayCrawler(CrawlerBase):
    expected_name = 'BitBay'
    schema = {'bids': [], 'asks': []}

    def __init__(self, exchange):
        super().__init__(exchange)

        if self.exchange.name != BitBayCrawler.expected_name:
            raise TypeError('Mismatched Exchange')

