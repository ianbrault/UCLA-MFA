"""
logger.py
handle file & console logging

author: Ian Brault <ianbrault@ucla.edu>
created: 19 May 2018
"""

import logging
import os.path

logfmt = logging.Formatter(fmt="[%(asctime)s]: %(message)s", datefmt='%I:%M:%S')
log = logging.getLogger()
log.setLevel(logging.INFO)

# log to file
logPath = os.path.dirname(os.path.realpath(__file__)) + "/server.log"
fileLog = logging.FileHandler(logPath)
fileLog.setFormatter(logfmt)
log.addHandler(fileLog)

# log to console
consLog = logging.StreamHandler()
consLog.setFormatter(logfmt)
log.addHandler(consLog)
