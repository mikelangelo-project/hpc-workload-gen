
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


def setLogLevel(logLevel=os.getenv('log_level', logging.WARNING), moduleName=None):
    # module name provided ?
    if moduleName is None:
        modList = [
            "ssh", "rsync", "sh",
            "sh.stream_bufferer", "sh.streamreader",
            "sh.command.process", "sh.command.process.streamreader",
            "api.hpc_backend", "api.experiment_config", "api.hpc_config" ]
    else:
        modList = [ moduleName ]

    # set log level
    for module in modList:
        try:
            lgr = logging.getLogger(module)
            lgr.setLevel(logLevel)
        except Exception as e:
            pass

