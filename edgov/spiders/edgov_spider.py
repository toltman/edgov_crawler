from twisted.internet.error import TimeoutError, TCPTimedOutError
from twisted.internet.error import DNSLookupError
from scrapy.spidermiddlewares.httperror import HttpError
import scrapy
import logging
import csv
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
    # not case sensitive
    return any([str(link).lower().endswith(data_type) for data_type in FILE_TYPES])


# link extractor for ed.gov domain
edgov_extractor = LinkExtractor(
    allow_domains='ed.gov',
    deny_domains=['www.eric.ed.gov', 'eric.ed.gov']
)

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

    start_urls = ['http://www.ed.gov']

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
            yield scrapy.Request(next_page, self.parse, errback=self.parse_error)

    def parse_error(self, failure):

        if failure.check(HttpError):
            response = failure.value.response
            with open('http_errors.csv', 'a+', newline='') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow([response.status, response.url])

        elif failure.check(DNSLookupError):
            # this is the original request
            request = failure.request
            with open('errors.csv', 'a+', newline='') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(['DNSLookupError', request.url])

        elif failure.check(TimeoutError, TCPTimedOutError):
            request = failure.request
            with open('errors.csv', 'a+', newline='') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(['TimeoutError', request.url])


class ErrbackSpider(scrapy.Spider):
    # this class is for testing
    name = "errback_example"
    start_urls = [
        "http://www.httpbin.org/",              # HTTP 200 expected
        "http://www.httpbin.org/status/404",    # Not found error
        "http://www.httpbin.org/status/500",    # server issue
        "http://www.httpbin.org:12345/",        # non-responding host, timeout expected
        "http://www.httphttpbinbin.org/",       # DNS error expected
    ]

    def start_requests(self):
        for u in self.start_urls:
            yield scrapy.Request(u, callback=self.parse_httpbin,
                                 errback=self.errback_httpbin,
                                 dont_filter=True)

    def parse_httpbin(self, response):
        self.logger.info(
            'Got successful response from {}'.format(response.url))
        # do something useful here...

    def errback_httpbin(self, failure):
        # log all failures
        self.logger.error(repr(failure))
        self.logger.error(failure.request.meta)

        # in case you want to do something special for some errors,
        # you may need the failure's type:

        if failure.check(HttpError):
            response = failure.value.response
            with open('http_error.csv', 'a+', newline='') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow([response.url, response.status])

        elif failure.check(DNSLookupError):
            # this is the original request
            request = failure.request
            self.logger.error('DNSLookupError on %s', request.url)

        elif failure.check(TimeoutError, TCPTimedOutError):
            request = failure.request
            self.logger.error('TimeoutError on %s', request.url)
