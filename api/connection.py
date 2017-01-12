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


class HLRS(object):
    """HLRS connection."""

    def __init__(self):
        """Initialize connection object."""
        self.logger = self.__get_logger()
        self.host = ssh.bake('-n', 'vsbase2')

    def __get_logger(self):
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

    def wait_for_job(self, job_id):
        """Wait for the job to finish."""
        job_running = True

        self.logger.info('Start waiting for job %s' % job_id)

        while job_running:
            self.logger.info('sleeping for x seconds\n\n')
            sleep(3)
            try:
                self.logger.debug('getting qstat infos')
                ssh_output = self.host(
                    "/opt/torque/current/server/bin/qstat", job_id)

                self.logger.debug('ssh return code: %s' % ssh_output.exit_code)
                self.logger.debug('type of the return %s' % type(ssh_output))
                self.logger.debug('qstat output:\n%s' % ssh_output)

                if ssh_output != '':
                    # slice the header and the last line which is empty
                    jobs_displayed = ssh_output.split('\n')[2:-1]
                    for job in jobs_displayed:
                        # remove whitespace
                        job_info = ' '.join(job.split())
                        # split into stuff
                        (job_id,
                            job_name,
                            job_user,
                            job_time,
                            job_status,
                            job_queue) = job_info.split(' ')
                        self.logger.debug(
                            'job %s has status %s' % (job_id, job_status))
                        if job_status == 'R' or job_status == 'S':
                            self.logger.debug(
                                '%s is running or scheduled' % job_id)
                        elif job_status == 'E':
                            self.logger.debug(
                                '%s is ended, waiting for complete.' % job_id)
                        elif job_status == 'C':
                            self.logger.debug(
                                '%s is complete. exit loop' % job_id)
                            job_running = False
                        else:
                            self.logger.error(
                                '%s in an unknown stat %s' % (
                                    job_id, job_status))
                else:
                    self.logger.debug(
                        'no job %s found, amuse finished' % job_id)
                    job_running = False

            except ErrorReturnCode as e:
                self.logger.error('\nError in ssh call:\n%s' % e)
                print e.stderr
                exit(1)

        self.logger.info('Job finished. Unblocking now.')

    def __build_qsub_args(self, workload_generator):
        """Build a list of arguments passed to qsub."""
        arg_list = []
        self.logger.info('arg_list building arg_list')

        if not workload_generator.get_params(
                'qsub_number_of_processes_per_node'):
            nodes = workload_generator.get_params('qsub_number_of_nodes')
            arg_list.append('-l')  # indicate additional parameter
            arg_list.append('nodes=%s' % nodes)
            self.logger.debug('arg_list: %s' % arg_list)

        else:
            nodes = workload_generator.get_params('qsub_number_of_nodes')
            ppn = workload_generator.get_params(
                'qsub_number_of_processes_per_node')
            arg_list.append('-l')  # indicate additional parameter
            arg_list.append('nodes=%s:ppn=%s' % (nodes, ppn))
            self.logger.debug('arg_list: %s' % arg_list)

        if workload_generator.get_vtorque():
            vtorque = workload_generator.get_vtorque()
            arg_list.append('-vm')  # indicates an vm job
            # get the keys (all are optional, swappable)
            arg_list_vtorque = []
            for key in vtorque:
                arg_list_vtorque.append('%s=%s' % (key, vtorque[key]))
            arg_list.append(','.join(arg_list_vtorque))
            self.logger.debug('arg_list= %s' % arg_list)

        return arg_list

    def submit_job(self, workload_generator):
        """Submit the job to qsub, returns job_id."""
        self.logger.info('Submitting job ...')

        job_script_path = '~/'
        job_script_path += str(
            workload_generator.get_params('experiment_dir')
        ).replace('./', '')  # removing possible ./ in the beginning
        job_script_path += '/'
        job_script_path += workload_generator.get_params('job_script_name')

        arg_list = self.__build_qsub_args(workload_generator)
        arg_list.append(job_script_path)
        self.logger.debug('arg_liste: %s' % arg_list)

        try:
            self.logger.debug(
                '/opt/dev/vTorque/src/qsub %s' % arg_list)

            # Job submit
            ssh_output = self.host(
                '/opt/dev/vTorque/src/qsub',
                *arg_list)

            self.logger.debug('ssh return code: %s' % ssh_output.exit_code)
            self.logger.debug('type of the return %s' % type(ssh_output))
            self.logger.debug('ssh_output output:\n%s' % ssh_output)

            # searching job id
            for line in ssh_output:
                self.logger.debug('looking at job id in \n%s' % line)

                if "hlrs.de" in line:
                    self.logger.debug('possible job id found: %s' % line)
                    return line

            self.logger.error(
                'no job id found in \n%s\nexiting!!!' % ssh_output)
            exit(1)

        except ErrorReturnCode as e:
            self.logger.error('\nError in ssh call:\n%s' % e)
            print e.stderr
            exit(1)

    def move_input(self, workload_generator, datadir):
        """Move the input files to the remote system."""
        job_script_dir_path = datadir + '/'
        job_script_dir_path += workload_generator.get_params('experiment_dir')

        # remove last / from input path
        if job_script_dir_path.endswith('/'):
            self.logger.info('removing / in %s' % job_script_dir_path)
            job_script_dir_path = job_script_dir_path[:-1]
            self.logger.info('new path is %s' % job_script_dir_path)

        remote_path = 'vsbase2:~/'
        # move job script
        self.logger.info(
            'moving date from %s to %s' % (job_script_dir_path, remote_path))
        rsync_output = rsync(
            "-azv", "--delete", job_script_dir_path, remote_path)

        self.logger.debug('rsync output:\n%s' % rsync_output)

        # testing rsync output
        if rsync_output == '':
            self.logger.error('rsync_output empty!!! exiting')
            exit(1)

        if rsync_output.exit_code != 0:
            self.logger.error('Rsync faild!')
            exit(1)

    def get_output_log(self):
        """Collect the output log form the remote system."""
        remote_log = ''
        raise NotImplementedError
        return remote_log

    def clean_remote(self):
        """Remove all files that are generated during the run."""
        raise NotImplementedError
