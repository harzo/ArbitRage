from exchanges_crawler.crawlers.crawlerbase import CrawlerBase


class BitBayCrawler(CrawlerBase):
    schema = {'bids': [], 'asks': []}

    def __init__(self, exchange):
        super().__init__(exchange)
