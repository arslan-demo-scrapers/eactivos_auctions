from scrapy.crawler import CrawlerProcess

from eactivos_auctions_spider import EactivosAuctionsSpider


def run_spider_via_python_script():
    process = CrawlerProcess()
    process.crawl(EactivosAuctionsSpider)
    process.start()


if __name__ == "__main__":
    run_spider_via_python_script()
