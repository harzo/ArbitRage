import asyncio
import sys
from exchanges.models import Exchange
from exchanges_crawler.crawlers.bitbay_crawler import BitBayCrawler
from exchanges_crawler.crawlers.cexio_crawler import CexioCrawler
from exchanges_crawler.crawlers.bitstamp_crawler import BitstampCrawler
from exchanges_crawler.crawlers.kraken_crawler import KrakenCrawler
from exchanges_crawler.crawlers.fiat_crawler import FiatCrawler


def init_crawlers():
    exchanges = Exchange.objects.filter(active=True).all()
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
#     ('0 */6 * * *', 'exchanges_crawler.runner.update_fiats')
# ]
def update_fiats_runner():
    exchange = Exchange.objects.filter(name="Fiat").first()
    crawlers = []
    if exchange:
        crawlers.append(FiatCrawler(exchange))

    _update_tickers(crawlers)


# Add to settings.py
# CRONJOBS = [
#     ('*/3 * * * *', 'exchanges_crawler.runner.update_tickers_runner')
# ]
def update_tickers_runner():
    crawlers = init_crawlers()
    _update_tickers(crawlers)


# Add to settings.py
# CRONJOBS = [
#     ('*/3 * * * *', 'exchanges_crawler.runner.update_orderbooks_runner')
# ]
def update_orderbooks_runner():
    crawlers = init_crawlers()
    _update_orderbooks(crawlers)


# Add to settings.py
# CRONJOBS = [
#     ('*/3 * * * *', 'exchanges_crawler.runner.update_all_runner')
# ]
def update_all_runner():
    crawlers = init_crawlers()

    _update_orderbooks(crawlers)
    _update_tickers(crawlers)


def _update_orderbooks(crawlers):
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


def _update_tickers(crawlers):
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