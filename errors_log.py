import re

with open('errors_output.txt', 'a+') as errorfile:
    with open("edgov_error_log.log") as logfile:
        for line in logfile:
            if ' ERROR: ' in line:
                errorfile.write(line)
