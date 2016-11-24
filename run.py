#!/usr/bin/env python
"""Tests the qstat function."""

# @Author: Uwe Schilling
# @Date: 2016-11-22


import logging
from api.ci import Workload
from api.connection import HLRS
from getopt import getopt, GetoptError
from sys import exit, argv


def get_logger(debug_lvl='DEBUG'):
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


def stage_in(conn, workload_generator, logger):
    """Move job files to the remote system, prepare everything."""
    logger.info('Starting stage in')
    conn.move_input(workload_generator)


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


def usage():
    """Print the usage of this script."""
    print(
        'This is the Workload generatar to submit job to HLRS\n'
        'run.py -w <workload_path.yaml> -m <mongodb://mongodb:27017>')


def extract_args(argv, logger):
    """Extract the provided arguments."""
    logger.debug('Trying to extract the needed arguments. -> %s' % argv)
    arguments = {}
    try:
        opts, args = getopt(argv[1:], "hw:m:", ["help", "workload="])
        logger.debug('getopt return: \nopts: %s\n args: %s' % (opts, args))
    except GetoptError as err:
        logger.error('Arg parsing failed! Exiting !!!')
        logger.debug('Revised error:\n%s' % str(err))
        usage()
        exit(2)
    logger.debug('Loop over opts: %s' % opts)
    for opt, arg in opts:
        logger.debug('opt: %s arg: %s' % (opt, arg))
        if opt in ("-h", "--help"):
            logger.warn('found help. Printing usage and exit.')
            usage()
            exit()
        elif opt in ("-w", "--workload"):
            arguments['workload'] = arg.rstrip("/")
            logger.info('found workload: %s' % arguments['workload'])
        else:
            logger.warn('no suitable arg found. print usage and exit.')
            usage()
            exit(2)
    logger.debug('returning found args')
    return arguments['workload']


def main():
    """The main program."""
    debug_lvl = 'INFO'
    logger = get_logger(debug_lvl)

    # get arguments
    provided_args = extract_args(argv, logger)

    # Pars yuml
    workload_generator = Workload(provided_args, debug_lvl)

    # Build connection
    conn = HLRS()

    # moving files
    stage_in(conn, workload_generator, logger)

    # runing workload
    job_id = run_test(conn, workload_generator, logger)

    # collecting output and cleaning up
    stage_out(job_id, conn, workload_generator, logger)

    logger.info('Test complete. Exiting main()')


if __name__ == '__main__':
    main()
