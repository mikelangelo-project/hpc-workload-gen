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

"""Package to hold classes for the connection to HLRS."""

# @Author: Uwe Schilling, schilling@hlrs.de
# @COMPANY: HLRS, University of Stuttgart
# @Date: 2016-11-22


import logging
from time import sleep
from sh import ssh, ErrorReturnCode, rsync


class HPCconnection(object):
    """Connect to the hpc system."""

    def __init__(self, workload_generator, host):
        """Initialize connection object."""
        self.logger = self._get_logger()
        self.workload_generator = workload_generator
        self.host = host
        self.ssh_host = ssh.bake('-n', host)
        self.job_id = ''  # init empty first

    def _get_logger(self):
        """Setup the global logger."""
        # log setup
        logger = logging.getLogger(__name__)

        logger.setLevel(logging.INFO)
        # create console handler with a higher log level
        ch = logging.StreamHandler()
        ch.setLevel(logging.INFO)
        # create formatter and add it to the handlers
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        ch.setFormatter(formatter)
        # add the handlers to the logger
        logger.addHandler(ch)
        logger.debug('Logger setup complete. Start Program ... ')
        return logger

    def _get_qstat_job_state(self):
        try:
            self.logger.debug('getting qstat infos')
            ssh_output = self.ssh_host(
                "/opt/torque/current/server/bin/qstat", self.job_id)

            self.logger.debug('qstat output:\n{}'.format(ssh_output))

            if ssh_output != '':
                # slice the header and the last line which is empty
                jobs_displayed = ssh_output.split('\n')[2:-1]
                for job in jobs_displayed:
                    # remove whitespace
                    job_info = ' '.join(job.split())
                    # split into stuff
                    (self.job_id,
                        job_name,
                        job_user,
                        job_time,
                        job_status,
                        job_queue) = job_info.split(' ')
                    self.logger.debug(
                        'job {} has status {}'.format(self.job_id, job_status))

                    return job_status
            else:
                return None

        except ErrorReturnCode as e:
            self.logger.error('\nError in ssh call:\n{}'.format(e))
            print e.stderr
            exit(1)

    def _is_qstat_job_running(self):
        job_status = self._get_qstat_job_state()

        if job_status == 'R' or job_status == 'S':
            self.logger.debug(
                '{} is running or scheduled'.format(self.job_id))
            return True
        elif job_status == 'E':
            self.logger.debug(
                '{} is ended, waiting for complete.'.format(self.job_id))
            return True
        elif job_status == 'Q':
            self.logger.debug(
                '{} is queued. waiting for start'.format(self.job_id))
            return True
        elif job_status == 'C':
            self.logger.debug(
                '{} is complete. exit loop'.format(self.job_id))
            return False
        elif job_status is None:
            self.logger.debug(
                'no job {} found, assume finished'.format(self.job_id))
            return False
        else:
            self.logger.error(
                '{} in an unknown stat {}'.format(self.job_id, job_status))
            return False

    def wait_for_job(self):
        """Wait for the job to finish."""
        job_running = True

        self.logger.info('Start waiting for job {}'.format(self.job_id))
        sleeping_time = 5  # seconds
        while job_running:
            self.logger.info('sleeping for {} seconds'.format(sleeping_time))
            sleep(sleeping_time)
            job_running = self._is_qstat_job_running()

        self.logger.info('Job finished. Unblocking now.')

    def _build_qsub_args(self):
        """Build a list of arguments passed to qsub."""
        arg_list = []
        self.logger.info('arg_list building arg_list')

        if not self.workload_generator.get_params(
                'qsub_number_of_processes_per_node'):
            nodes = self.workload_generator.get_params('qsub_number_of_nodes')
            arg_list.append('-l')  # indicate additional parameter
            arg_list.append('nodes={}'.format(nodes))
            self.logger.debug('arg_list: {}'.format(arg_list))

        else:
            nodes = self.workload_generator.get_params('qsub_number_of_nodes')
            ppn = self.workload_generator.get_params(
                'qsub_number_of_processes_per_node')
            arg_list.append('-l')  # indicate additional parameter
            arg_list.append('nodes={}:ppn={}'.format(nodes, ppn))
            self.logger.debug('arg_list: {}'.format(arg_list))

        if self.workload_generator.get_vtorque():
            vtorque = self.workload_generator.get_vtorque()
            arg_list.append('-vm')  # indicates an vm job
            # get the keys (all are optional, swappable)
            arg_list_vtorque = []
            for key in vtorque:
                arg_list_vtorque.append('{}={}'.format(key, vtorque[key]))
            arg_list.append(','.join(arg_list_vtorque))
            self.logger.debug('arg_list= {}'.format(arg_list))
        self.logger.debug('returning arg list = {}'.format(arg_list))
        return arg_list

    def _get_job_script_path(self):
        job_script_path = '~/'
        job_script_path += str(
            self.workload_generator.get_params('experiment_dir')
        )
        # removing possible ./ in the beginning
        job_script_path = job_script_path.replace('./', '')
        job_script_path += '/'
        job_script_path += self.workload_generator.get_params(
            'job_script_name'
        )
        return job_script_path

    def submit_job(self):
        """Submit the job to qsub, returns job_id."""
        self.logger.info('Submitting job ...')

        job_script_path = self._get_job_script_path()

        arg_list = self._build_qsub_args()
        arg_list.append(job_script_path)
        self.logger.debug('arg_liste: {}'.format(arg_list))

        try:
            self.logger.debug(
                '/opt/dev/vTorque/src/qsub {}'.format(arg_list)
            )

            # Job submit
            ssh_output = self.ssh_host('/opt/dev/vTorque/src/qsub', *arg_list)

            # searching job id
            for line in ssh_output:
                self.logger.debug('searching for job id in \n{}'.format(line))

                if "hlrs.de" in line:
                    self.logger.debug('possible job id found: {}'.format(line))
                    self.job_id = str(line)
                    return

            self.logger.error(
                'no job id found in \n{}\nexiting!!!'.format(ssh_output)
            )
            exit(1)

        except ErrorReturnCode as e:
            self.logger.error('\nError in ssh call:\n{}'.format(e))
            print e.stderr
            exit(1)

    def move_input(self, datadir):
        """Move the input files to the remote system."""
        experiment_dir = self.workload_generator.get_params(
            'experiment_dir'
        )
        job_script_dir_path = datadir + '/'
        job_script_dir_path += experiment_dir

        # remove last / from input path
        if not job_script_dir_path.endswith('/'):
            self.logger.info('adding / in {}'.format(job_script_dir_path))
            job_script_dir_path = job_script_dir_path + '/'
            self.logger.info('new path is {}'.format(job_script_dir_path))

        remote_path = '{}:~/'.format(self.host)
        remote_path += experiment_dir
        # move job script
        self.logger.info(
            'moving date from {} to {}'.format(
                job_script_dir_path, remote_path
            )
        )
        # create remote dir first
        self.ssh_host(
            "mkdir",
            "-p",
            experiment_dir
        )

        rsync_output = rsync(
            "-azv", "--delete", job_script_dir_path, remote_path)

        self.logger.debug('rsync output:\n{}'.format(rsync_output))

        # testing rsync output
        if rsync_output == '':
            self.logger.error('rsync_output empty!!! exiting')
            exit(1)

        if rsync_output.exit_code != 0:
            self.logger.error('Rsync faild!')
            exit(1)

    def _get_output_log(self, log_path):
        """Collect the output log form the remote system."""
        remote_log = self.ssh_host('cat', log_path)
        return remote_log

    def _get_std_log_path(self, log_type):
        """Build log path with logtype option."""
        if log_type == 'STDIN':
            log_type_string = 'o'
        elif log_type == 'STDERR':
            log_type_string = 'e'
        else:
            self.logger.error('Unknown log type, {}'.format(log_type))

        job_script_name = self.workload_generator.get_params('job_script_name')
        job_number = str(self.job_id).replace('.vsbase2', '')
        log_path = '~/{}.{}{}'.format(job_script_name,
                                      log_type_string,
                                      job_number)

        self.logger.debug('returning {} as path for log-file'.format(log_path))
        return log_path

    def _get_qsub_log_path(self):
        vtorque = self.workload_generator.get_vtorque()
        self.logger.debug('getting vtorque as {}'.format(vtorque))
        if self.workload_generator.get_vtorque() is not None:
            base_path = '~/.vtorque'  # TODO replace by config file
            return '{}/{}.hlrs.de/debug.log'.format(base_path, self.job_id)

    def _print_log_file(self, log_type, log_file):
        """Collect and print the stdin log from qsub."""
        self.logger.info(
            '\n'
            '----------------------------------------------\n'
            'Contend of log: {}\n'
            '----------------------------------------------\n'.format(log_type)
        )
        for line in log_file:
            print unicode(line).rstrip()

        self.logger.info(
            '\n'
            '----------------------------------------------\n')

    def print_log(self, log_type):
        """Switch for different log types."""
        if log_type == 'STDIN' or log_type == 'STDERR':
            log_path = self._get_std_log_path(log_type)

        elif log_type == 'QSUB_LOG':
            log_path = self._get_qsub_log_path()
        elif log_type == 'APP_LOG':
            log_path = self.workload_generator.get_params('application_log')
        else:
            self.logger.error('Unknown log type, {}'.format(log_type))
            exit(1)

        if log_path is None:
            self.logger.info('No log for {}'.format(log_type))
        else:
            log_file = self._get_output_log(log_path)
            self._print_log_file(log_type, log_file)

    def clean_remote(self):
        """Remove all files that are generated during the run."""
        raise NotImplementedError
