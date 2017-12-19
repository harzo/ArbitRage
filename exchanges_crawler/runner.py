import asyncio
import sys
from exchanges.models import Exchange
from exchanges_crawler.crawlers.bitbay_crawler import BitBayCrawler
from exchanges_crawler.crawlers.cexio_crawler import CexioCrawler
from exchanges_crawler.crawlers.bitstamp_crawler import BitstampCrawler
from exchanges_crawler.crawlers.kraken_crawler import KrakenCrawler


def init_crawlers():
    exchanges = Exchange.objects.all()
    crawlers = []
    for exchange in exchanges:
        try:
            crawler_class = eval(exchange.name + 'Crawler')
        except NameError:
            continue

        crawlers.append(crawler_class(exchange))

    return crawlers


# Add to settings.py
# CRONJOBS = [
#     ('*/5 * * * *', 'exchanges_crawler.runner.update_all')
# ]
def update_all():
    crawlers = init_crawlers()

    update_orderbooks(crawlers)
    update_tickers(crawlers)


def update_orderbooks(crawlers):
    if sys.platform == 'win32':
        loop = asyncio.ProactorEventLoop()
    else:
        loop = asyncio.new_event_loop()

    tasks = []
    for c_idx in range(len(crawlers)):
        tasks.append(crawlers[c_idx].get_orderbooks())

    asyncio.set_event_loop(loop)
    try:
        loop.run_until_complete(asyncio.gather(*tasks))
    finally:
        loop.close()


def update_tickers(crawlers):
    if sys.platform == 'win32':
        loop = asyncio.ProactorEventLoop()
    else:
        loop = asyncio.new_event_loop()

    tasks = []
    for c_idx in range(len(crawlers)):
        tasks.append(crawlers[c_idx].get_tickers())

    asyncio.set_event_loop(loop)
    try:
        loop.run_until_complete(asyncio.gather(*tasks))
    finally:
        loop.close()