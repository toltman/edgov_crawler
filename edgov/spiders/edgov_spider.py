import scrapy
from scrapy.linkextractors import LinkExtractor

# list of data types
FILE_TYPES = [
    '.xls',
    '.csv',
    '.sas',
    '.dat',
    '.spss',
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
        'https://nces.ed.gov/programs/digest/d18/tables/dt18_326.10.asp',
    ]

    custom_settings = {
        'DEPTH_LIMIT': 1,
        'DEPTH_PRIORITY': 1,
    }

    def parse(self, response):
        for link in data_extractor.extract_links(response):
            if is_data_file(link.url):
                yield {
                    response.url: link.url
                }
        for next_page in edgov_extractor.extract_links(response):
            yield response.follow(next_page, self.parse)
