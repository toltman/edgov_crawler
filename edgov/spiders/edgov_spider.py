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
    '.sav',
    '.dta',
    '.do',
    '.r',
    '.rdata',
    '.rda',
    '.sd2',
    '.sd7',
    '.sas7bdat',
]


def is_data_file(link):
    # Returns True if the file type of link matches any of the data file types
    return any([str(link).lower().endswith(data_type) for data_type in FILE_TYPES])


edgov_extractor = LinkExtractor(allow_domains='ed.gov')

data_extractor = LinkExtractor(
    allow_domains='ed.gov',
    deny_extensions=[]
)

logger = logging.getLogger()

debug_log = logging.FileHandler('edgov.log')
debug_log.setLevel(logging.DEBUG)

error_log = logging.FileHandler('edgov_error_log.log')
error_log.setLevel(logging.ERROR)

formatter = logging.Formatter(
    '%(asctime)s [%(name)s] %(levelname)s: %(message)s')

debug_log.setFormatter(formatter)
error_log.setFormatter(formatter)

logger.addHandler(debug_log)
logger.addHandler(error_log)


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
    }

    def parse(self, response):
        for link in data_extractor.extract_links(response):
            if is_data_file(link.url):
                yield {
                    'link': response.url,
                    'data_file': link.url
                }
        for next_page in edgov_extractor.extract_links(response):
            yield response.follow(next_page, self.parse)
