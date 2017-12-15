from exchanges.models import Exchange


class CrawlerBase:

    def __init__(self, exchange):
        if exchange.__class__ != Exchange:
            raise TypeError('Given argument is not Exchange type')

        self.exchange = exchange

