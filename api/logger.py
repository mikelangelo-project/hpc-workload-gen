


import logging

loggers = {}

def getLogger(name="HPC"):
    if not name in loggers:
        _initLogger(name)
    return loggers[name]


def _initLogger(name):
    """Setup the requested logger."""
    # log setup
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    # create console handler with a higher log level
    ch = logging.StreamHandler()
    if getenv('log_level'):
        ch.setLevel(logging[getenv('log_level')])
    else:
        ch.setLevel(logging.INFO)
    # create formatter and add it to the handlers
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    ch.setFormatter(formatter)
    # add the handlers to the logger
    logger.addHandler(ch)
    logger.debug('Logger initialized for \'{}\''.format(name))
    loggers[name] = logger