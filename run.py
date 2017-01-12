#!/usr/bin/env python
#
# Copyright 2016 HLRS, University of Stuttgart
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

"""Tests the qstat function."""

# @Author: Uwe Schilling, schilling@hlrs.de
# @COMPANY: HLRS, University of Stuttgart
# @Date: 2016-11-22


import logging
import click
from api.ci import Workload
from api.connection import HLRS


def get_logger():
    """Setup the global logger."""
    # log setup
    logger = logging.getLogger(__name__)

    logger.setLevel(logging.DEBUG)
    # create console handler with a higher log level
    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)
    # create formatter and add it to the handlers
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    ch.setFormatter(formatter)
    # add the handlers to the logger
    logger.addHandler(ch)
    logger.debug('Logger setup complete. Start Program ... ')
    return logger


def stage_in(conn, workload_generator, datadir, logger):
    """Move job files to the remote system, prepare everything."""
    logger.info('Starting stage in')
    conn.move_input(workload_generator, datadir)


def run_test(conn, workload_generator, logger):
    """Run the test on the remote system."""
    logger.info('Running Test')

    # Submitting
    job_id = conn.submit_job(workload_generator)

    logger.info('Submit successful start waiting for job to end.')

    # waiting for job until done
    conn.wait_for_job(job_id)

    logger.info('Job finished.')
    return job_id


def stage_out(job_id, conn, workload_generator, logger):
    """Clean up to a defined state."""
    logger.info('Starting stage out')

    logger.warn('skipping for the moment')


@click.command()
@click.option(
    '-w',
    '--workload',
    type=click.Path(exists=True),
    help='the path to the workload.yaml',
    required=True)
@click.option(
    '-d',
    '--datadir',
    type=click.Path(exists=True),
    help='base path containing the experiment',
    required=True)
def main(workload, datadir):
    """The main program."""
    logger = get_logger()

    # Pars yuml
    workload_generator = Workload(workload)

    # Build connection
    conn = HLRS()

    # moving files
    stage_in(conn, workload_generator, datadir, logger)

    # runing workload
    job_id = run_test(conn, workload_generator, logger)

    # collecting output and cleaning up
    stage_out(job_id, conn, workload_generator, logger)

    logger.info('Test complete. Exiting main()')


if __name__ == '__main__':
    main()
