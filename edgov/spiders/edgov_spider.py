import scrapy
import logging
from scrapy.linkextractors import LinkExtractor

# list of data types
FILE_TYPES = [
    '.xls',
    '.csv',
    '.sas',
    '.dat',
    '.spss',
    '.sps',
    '.db',
    '.sql',
    '.xml',
    '.xlsx',
    '.zip',
]


def is_data_file(link):
    # Returns True if the file type of link matches any of the data file types
    return any([str(link).endswith(data_type) for data_type in FILE_TYPES])


edgov_extractor = LinkExtractor(allow_domains='ed.gov')

data_extractor = LinkExtractor(
    allow_domains='ed.gov',
    deny_extensions=[]
)


class EdgovSpider(scrapy.Spider):
    name = "edgov"

    start_urls = [
        'https://www.ed.gov',
    ]

    custom_settings = {
        'DEPTH_LIMIT': 0,
        'DEPTH_PRIORITY': 1,
        'SCHEDULER_DISK_QUEUE': 'scrapy.squeues.PickleFifoDiskQueue',
        'SCHEDULER_MEMORY_QUEUE': 'scrapy.squeues.FifoMemoryQueue',
        'SCHEDULER_DEBUG': True,
        'LOG_FILE': 'edgov.log'
    }

    logging.getLogger().addHandler(logging.StreamHandler())

    def parse(self, response):
        for link in data_extractor.extract_links(response):
            if is_data_file(link.url):
                yield {
                    'link': response.url,
                    'data_file': link.url
                }
        for next_page in edgov_extractor.extract_links(response):
            yield response.follow(next_page, self.parse)
