


import logging
import os
import sh

loggers = {}

def getLogger(name="HPC"):
    if not name in loggers:
        _initLogger(name)
    return loggers[name]


def _initLogger(name):
    """Setup the requested logger."""
    # log setup
    logger = logging.getLogger(name)
    logger.setLevel(logging.__dict__[os.getenv('log_level', 'INFO')])
    # create console handler with a higher log level
    ch = logging.StreamHandler()
    ch.setLevel(getattr(logging, os.getenv('log_level', 'INFO')))
    # create formatter and add it to the handlers
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    ch.setFormatter(formatter)
    # add the handlers to the logger
    logger.addHandler(ch)
    logger.debug('Logger initialized for \'{}\''.format(name))
    loggers[name] = logger
    # set log level for 'sh' (rsync/ssh) to WARNING
    logging.getLogger(sh.command.process).setLevel(logging.WARNING)
    logging.getLogger(rsync).setLevel(logging.WARNING)