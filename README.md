# edgov_crawler
Use the following command to run the program
```
scrapy crawl edgov -o links.csv -s JOBDIR=crawls/edgov-1
```
Edits to the spider should be made in `edgov/spiders/edgov_spider.py`

The spider searches for the following file types: 
```
'.xls', '.csv', '.sas', '.dat', '.spss', '.sps', '.db', '.sql', '.xml', 
'.xlsx', '.zip', '.sav', '.dta', '.do', '.r', '.rdata', '.rda', '.sd2', 
'.sd7', '.sas7bdat', '.mdb', '.accdb', '.txt', '.dct', '.tsv'
```
All subdomains of ed.gov are allowed except for the following: `'www.eric.ed.gov',  'eric.ed.gov', 'eddataexpress.ed.gov', 'ocrcas.ed.gov', 'statesupportnetwork.ed.gov', 'datainventory.ed.gov'`. These domains were excluded because they did not yield data files and the crawler spend an extraordinary amount of time crawling them. 

