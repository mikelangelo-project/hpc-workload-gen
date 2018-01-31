#!/usr/bin/env python
#
# Copyright 2018 HLRS, University of Stuttgart
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

"""Logger Manager"""

# @Author: Nico Struckmann, struckmann@hlrs.de
# @COMPANY: HLRS, University of Stuttgart
# @Date: 2018-01-31
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

    # create formatter and add it to the handlers
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    # log file
    logFile = os.getenv('log_file');
    if logFile:
        fh = logging.FileHandler(logFile)
        fh.setLevel(getattr(logging, os.getenv('log_level_file', 'DEBUG')))
        fh.setFormatter(formatter)
        logger.addHandler(fh)

    # print debug msg
    logger.debug('Logger initialized for \'{}\''.format(name))
    loggers[name] = logger


def setLogLevel(logLevel=None, moduleName=None, logFileFlag=false):

    # log_level provided ?
    if not logLevel:
        # no, use default
        if logFileFlag:
            logLevel = os.getenv('log_level_console', logging.WARNING)
        else:
            logLevel = os.getenv('log_level_file', logging.WARNING)
        logLevel = getattr(logging, logLevel)

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
        # get module'S logger
        log = logging.getLogger(module)
        # get all handlers
        for hdlr in log.handlers[:]:
            try:
                # log file or console handler ?
                if logFileFlag and isinstance(hdlr, logging.FileHandler):
                    hdlr.setLevel(logLevel)
                    break
                elif not logFileFlag:
                    hdlr.setLevel(logLevel)
                    break
            except Exception as e:
                pass

