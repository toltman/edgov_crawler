import re
from urllib.parse import urlparse
import pandas as pd

with open('errors.log', 'a+') as errorfile:
    with open("edgov.log") as logfile:
        for line in logfile:
            if ' ERROR: ' in line:
                errorfile.write(line)
