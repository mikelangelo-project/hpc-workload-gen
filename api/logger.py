
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

    # log file
    logFile = os.getenv('log_file');
    if logFile:
      fh = logging.FileHandler(logFile)
      fh.setLevel(getattr(logging, os.getenv('log_level_file', 'DEBUG')))

    # console log (lower level as default)
    ch = logging.StreamHandler()
    ch.setLevel(getattr(logging, os.getenv('log_level_console', 'INFO')))

    # create formatter and add it to the handlers
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    # apply handlers
    if logFile:
        fh.setFormatter(formatter)
        logger.addHandler(fh)
    logger.addHandler(ch)

    # print debug msg
    logger.debug('Logger initialized for \'{}\''.format(name))
    loggers[name] = logger


def setLogLevel(logLevel=None, moduleName=None):

    # log_level provided or use defaults ?
    logLevelFile = os.getenv('log_level_file', logging.DEBUG)
    logLevelCons = os.getenv('log_level_console', logging.WARNING)

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
            lgr.setLevel(logLevelFile)
            lgr.setLevel(logLevelCons)
        except Exception as e:
            pass

