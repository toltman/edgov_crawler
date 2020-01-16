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
    '.mdb',
    '.accdb',
    '.txt',
    '.dct',
    '.tsv'
]


def is_data_file(link):
    # Returns True if the file type of link matches any of the data file types
    # not case sensitive
    return any([str(link).lower().endswith(data_type) for data_type in FILE_TYPES])


# link extractor for ed.gov domain
edgov_extractor = LinkExtractor(
    deny=r'https://nces.ed.gov/COLLEGENAVIGATOR\.*',
    allow_domains='ed.gov',
    deny_domains=[
        'www.eric.ed.gov', 
        'eric.ed.gov',
        'eddataexpress.ed.gov', 
        'ocrcas.ed.gov', 
        'statesupportnetwork.ed.gov',
        'datainventory.ed.gov'
    ],
    deny_extensions=[
        # archives
        '7z', '7zip', 'bz2', 'rar', 'tar', 'tar.gz', 'xz', 'zip',

        # images
        'mng', 'pct', 'bmp', 'gif', 'jpg', 'jpeg', 'png', 'pst', 'psp', 'tif',
        'tiff', 'ai', 'drw', 'dxf', 'eps', 'ps', 'svg', 'cdr', 'ico',

        # audio
        'mp3', 'wma', 'ogg', 'wav', 'ra', 'aac', 'mid', 'au', 'aiff',

        # video
        '3gp', 'asf', 'asx', 'avi', 'mov', 'mp4', 'mpg', 'qt', 'rm', 'swf', 'wmv',
        'm4a', 'm4v', 'flv', 'webm',

        # office suites
        'xls', 'xlsx', 'ppt', 'pptx', 'pps', 'doc', 'docx', 'odt', 'ods', 'odg',
        'odp',

        # other
        'css', 'pdf', 'exe', 'bin', 'rss', 'dmg', 'iso', 'apk',

        # added
        'csv', 'sas', 'dat', 'spss', 'sps', 'db', 'sql', 'xml', 'zip', 'sav',
        'dta', 'do', 'r', 'rdata', 'rda', 'sd2', 'sd7', 'sas7bdat', 'mdb', 'accdb',
        'txt', 'dct', 'tsv'
    ]
)

data_extractor = LinkExtractor(
    allow_domains='ed.gov',
    deny_extensions=[]
)

logger = logging.getLogger()

debug_log = logging.FileHandler('edgov.log')
debug_log.setLevel(logging.DEBUG)

# error_log = logging.FileHandler('edgov_error_log.log')
# error_log.setLevel(logging.ERROR)

formatter = logging.Formatter(
    '%(asctime)s [%(name)s] %(levelname)s: %(message)s'
)

debug_log.setFormatter(formatter)
# error_log.setFormatter(formatter)

logger.addHandler(debug_log)
# logger.addHandler(error_log)


class EdgovSpider(scrapy.Spider):
    name = "edgov"

    start_urls = ['https://www.ed.gov/']

    custom_settings = {
        'DEPTH_LIMIT': 0,
        'DEPTH_PRIORITY': 1,
        'SCHEDULER_DISK_QUEUE': 'scrapy.squeues.PickleFifoDiskQueue',
        'SCHEDULER_MEMORY_QUEUE': 'scrapy.squeues.FifoMemoryQueue',
        'SCHEDULER_DEBUG': True,
        'DOWNLOAD_MAXSIZE': 5000000,
        'DOWNLOAD_WARNSIZE': 3000000,
        'MEMDEBUG_ENABLED': True
    }

    def parse(self, response):
        for link in data_extractor.extract_links(response):
            if is_data_file(link.url):
                yield {
                    'link': response.url,
                    'data_file': link.url
                }
        for next_page in edgov_extractor.extract_links(response):
            yield scrapy.Request(next_page.url, self.parse, errback=self.parse_error)

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
