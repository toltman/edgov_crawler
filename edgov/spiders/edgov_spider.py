import scrapy


class EdgovSpider(scrapy.Spider):
    name = "edgov"

    start_urls = [
        'http://ed.gov',
    ]

    def parse(self, response):
        for link in response.css('a::attr(href)'):
            yield {
                "link": response.urljoin(link.get()),
            }
