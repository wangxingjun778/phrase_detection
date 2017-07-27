import logging
import os
import sys
from logging.handlers import TimedRotatingFileHandler

def set_logger(filename):
    logger = logging.getLogger()
    if filename[0] == '/':
        logsdir, logsfile = os.path.split(filename)
        if not os.path.exists(logsdir):
            os.makedirs(logsdir, mode = 0775)
    else:
        logsdir, logsfile = os.path.split(sys.path[0] + '/' + filename)
        if not os.path.exists(logsdir):
            os.makedirs(logsdir, mode = 0775)

    hdlr = TimedRotatingFileHandler(filename, when = "midnight", interval = 1, backupCount = 7)
    fmt_str = '[%(levelname)s %(asctime)s @ %(process)d] - %(message)s'
    formatter = logging.Formatter(fmt_str)
    hdlr.setFormatter(formatter)
    logger.handlers = []
    logger.addHandler(hdlr)
    logger.setLevel(logging.DEBUG)

