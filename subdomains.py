import re
from urllib.parse import urlparse
import pandas as pd

hostnames = []

with open("edgov-1.log") as logfile:
    for line in logfile:
        m = re.search(r'DEBUG\: Crawled \(200\) <GET (.*)>', line)
        if m:
            hostnames.append(urlparse(m.group(1)).hostname)

s = pd.Series(hostnames)
print(s.value_counts().to_string())
