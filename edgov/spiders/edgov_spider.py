import scrapy
from scrapy.linkextractors import LinkExtractor


class EdgovSpider(scrapy.Spider):
    name = "edgov"

    start_urls = [
        'http://www.ed.gov',
    ]

    def parse(self, response):
        le = LinkExtractor(allow_domains='ed.gov')
        for link in le.extract_links(response):
            yield {
                "link": link.url,
            }
