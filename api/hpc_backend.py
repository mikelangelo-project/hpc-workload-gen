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

import sys
import os
from time import time, sleep
from sh import ssh, ErrorReturnCode, rsync

from api.logger import getLogger
from api.hpc_config import HPCBackendConfiguration




class HPCBackend(object):
    """HPC system back-end """

    def __init__(self, hpcCfg):
        """Initialize connection object."""
        self.logger = getLogger(__name__)
        assert hpcCfg is not None
        self.hpcConfig = hpcCfg
        self.logger.debug("SSH properties\n host: %s,\n user: %s,\n port: %s",
                          self.hpcConfig.get_value('host'),
                          self.hpcConfig.get_value('user_name'),
                          self.hpcConfig.get_value('ssh_port'))
        try:
            self.ssh_conn = ssh.bake('-n', self.hpcConfig.get_value('host'))
            self.ssh_conn = ssh.bake('-l', self.hpcConfig.get_value('user_name'))
            self.ssh_conn = ssh.bake('-p', self.hpcConfig.get_value('ssh_port'))
            self.ssh_conn = ssh.bake('-i', self.hpcConfig.get_value('ssh_key'))
            self.ssh_conn = ssh.bake(self.hpcConfig.get_value('host'))
        except ErrorReturnCode as e:
            self.logger.error('SSH initialization failed:\n{}'.format(e.stderr))
            sys.exit(1)

    def _get_job_state(self, experiment):
        """ Determines current job state with qstat"""
        try:
            self.logger.debug('getting qstat infos')
            ssh_output = self.ssh_conn(self.hpcConfig.path_qstat, experiment.get_stripped_job_id())

            self.logger.debug('qstat output:\n{}'.format(ssh_output))

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
                        job_state,
                        job_queue) = job_info.split(' ')
                    self.logger.debug(
                        'job {} is in state {}'.format(experiment.get_job_id(), job_state))
                    return job_state
            else:
                return None

        except ErrorReturnCode as e:
            self.logger.error('\nError checking job state:\n{}'.format(e.stderr))
            sys.exit(1)


    def _is_job_running(self, experiment):

        job_status = self._get_job_state(experiment)
        job_id = experiment.get_job_id()

        if job_status == 'Q':
            self.logger.debug(
                'Job with ID \'{}\' is queued.'.format(job_id))
            return True
        elif job_status == 'W':
            self.logger.debug(
                'Job with ID \'{}\' is waiting for execution'.format(job_id))
            return True
        if job_status == 'S':
            self.logger.debug(
                'Job with ID \'{}\' is starting.'.format(job_id))
            return True
        elif job_status == 'R':
            self.logger.debug(
                'Job with ID \'{}\' is running'.format(job_id))
            return True
        elif job_status == 'E':
            self.logger.debug(
                'Job with ID \'{}\' is finishing, waiting for completion.'.format(job_id))
            return True
        elif job_status == 'C':
            self.logger.debug(
                'Job with ID \'{}\' is completed.'.format(job_id))
            return False
        elif job_status == 'H':
            self.logger.error(
                'Job with ID \'{}\' is on hold, aborting.'.format(job_id))
            return False
        elif job_status is None:
            self.logger.debug(
                'Job ID \'{}\' not found, assume finished'.format(job_id))
            return False
        else:
            self.logger.error(
                '{} in an unknown state {}'.format(job_id, job_status))
            return False


    def _wait_for_job(self, experiment):
        """Wait for the job to finish."""
        self.logger.debug('Experiment job submitted, waiting for completion.')
        job_running = True

        self.logger.info('Waiting for job {} to complete.\nMay can take '
                         'quite some time, so please be patient ...'.format(experiment.get_job_id()))
        sleeping_time = 5  # seconds
        while job_running:
            self.logger.debug('sleeping for {} seconds'.format(sleeping_time))
            sleep(sleeping_time)
            job_running = self._is_job_running(experiment)

        self.logger.info('Job finished. Unblocking now.')


    def _build_qsub_args(self, experiment):
        """Build a list of arguments passed to qsub."""
        arg_list = []
        self.logger.debug('arg_list building arg_list')

        if experiment is None:
            self.logger.error("No experiment config.")
            sys.exit(1)

        qsub_args = experiment.get_qsub_args();
        if qsub_args is None:
            self.logger.warning("Parameter 'qsub_args' not found.")
        else:
            arg_list.append(qsub_args)

        vsub_args = experiment.get_vsub_args();
        if vsub_args is None:
            self.logger.warning("Parameter 'qsub_args' not found.")
        else:
            arg_list.append(vsub_args)

#        if 'vtorque' in experiment['params']:
#            vtorque = experiment['params']['vtorque']
#            arg_list.append('-vm')  # indicates an vm job
#            # get the keys (all are optional, swappable)
#            arg_list_vtorque = []
#            for key in vtorque:
#                arg_list_vtorque.append('{}={}'.format(key, vtorque[key]))
#           arg_list.append(','.join(arg_list_vtorque))
#           self.logger.debug('arg_list= {}'.format(arg_list))

        self.logger.debug('returning arg list = {}'.format(arg_list))
        return arg_list


    def _get_output_log(self, log_path):
        """Collect the output log form the remote system."""
        self.logger.info("Fetching remote log file '%s'", log_path)
        try:
            remote_log = self.ssh_conn('cat', log_path)
        except ErrorReturnCode as e:
            self.logger.error("Failed to fetch log file '%s' from HPC system, error msg:\n%s",
                              log_path, e.stderr)
            sys.exit(1)
        return remote_log


    def _get_std_log_path(self, log_type, experimentCfg):
        """Build log path with log type option."""
        if log_type == 'STDIN':
            log_type_string = 'o'
        elif log_type == 'STDERR':
            log_type_string = 'e'
        else:
            self.logger.error('Unknown log type, {}'.format(log_type))

        job_script = os.path.basename(experimentCfg.get_job_script())
        job_id = experimentCfg.get_stripped_job_id()
        log_path = '~/{}.{}{}'.format(job_script,
                                      log_type_string,
                                      job_id)

        self.logger.debug("Remote log file '{}' as path for log-file".format(log_path))
        return log_path


    def _get_vsub_debug_log_path(self, experiment):
        vtorque_args = experiment.get_vsub_args()
        self.logger.debug('getting vtorque as {}'.format(vtorque_args))
        if experiment.is_vm_job():
            return '{}/{}/debug.log'.format(
                self.hpcConfig.get_value('path_vtorque_log'),
                experiment.get_job_id()).replace('\n','')


    def _print_log_file(self, log_type, log_file):
        """Collect and print the stdin log from qsub."""
        self.logger.info(
            '\n'
            '----------------------------------------------\n'
            'Log file content: {}\n'
            '----------------------------------------------\n'.format(log_type)
        )
        print(log_file)
        self.logger.info(
            '\n'
            '----------------------------------------------\n')


    def _print_log(self, log_type, experiment):
        """Switch for different log types."""
        if log_type == 'STDIN' or log_type == 'STDERR':
            log_path = self._get_std_log_path(log_type, experiment)
        elif log_type == 'VTORQUE_DEBUG_LOG':
            log_path = self._get_vsub_debug_log_path(experiment)
        else:
            self.logger.error('Unknown log type, {}'.format(log_type))
            exit(1)
        #
        if log_path is None:
            self.logger.info('No log for {}'.format(log_type))
        else:
            log_file = self._get_output_log(log_path)
            self._print_log_file(log_type, log_file)


    def _submit_job(self, experiment):
        """Submit the job to qsub, returns job_id."""
        self.logger.info('Submitting experiment to HPC system.')

        job_script = os.path.basename(experiment.get_job_script())

        arg_list = self._build_qsub_args(experiment)
        arg_list.append(job_script)
        self.logger.info('Batch-System arguments:\n{}'.format(arg_list))

        try:
            self.logger.debug(
                '{} {}'.format(self.hpcConfig.path_qsub, arg_list)
            )

            # job submit depends on either vm job or not
            if experiment.is_vm_job():
                self.logger.info('VM job detected')
                submission_cmd = self.hpcConfig.path_vsub;
            else:
                submission_cmd = self.hpcConfig.path_qsub;
                self.logger.info('Bare-metal job detected.')
            self.logger.info(
                'using command \'{}\' for job submission.'.format(
                    submission_cmd))

            # get stating time and convert
            experiment.set_start_time(int(time()) * 1000)
            self.logger.debug(
                'stat time stamp: {}'.format(experiment.get_start_time())
            )
            ssh_output = self.ssh_conn(submission_cmd, arg_list)
            self.logger.debug("SSH output:\n%s", ssh_output)

            # searching job id
            for line in ssh_output:
                self.logger.debug('searching for job id in \n{}'.format(line))
                # job failed ?
                if "error" in line:
                    self.logger.info("Job submission failed!\n %s", line)
                    sys.exit(1)
                elif self.hpcConfig.domain in line:
                    self.logger.debug('Job id found: {}'.format(line))
                    experiment.set_job_id(str(line))
                    if self.hpcConfig.grafana:
                        self.logger.info(
                            'Job performance data at:\n'
                            '{}var-JobId=snapTask-{}-{}&'
                            'from={}&'
                            'to=now'.format(
                                self.hpcConfig.grafana_base_string,
                                self.hpcConfig.user_name,
                                experiment.get_job_id().rstrip(),
                                experiment.get_start_time()
                            )
                        )
                    return

            self.logger.error(
                'no job id found in \n{}\nexiting!'.format(ssh_output)
            )
            sys.exit(1)

        except ErrorReturnCode as e:
            self.logger.error('\nError in ssh call:\n{}'.format(e))
            print e.stderr
            sys.exit(1)


    def _stage_in_data(self, experimentCfg):
        """Move the input files to the remote system."""
        self.logger.info('Staging data into the HPC system..')
        experiment_dir = experimentCfg.get_input_data()
        job_script = experimentCfg.get_job_script()

        try:
            # transfer experiment data dir
            self.logger.debug("Staging experiment dir '{}' to HPC system..".format(experimentCfg.get_input_data()))
            rsync_output = rsync(
                "-azvrg", experimentCfg.get_input_data(), '{}@{}:{}'.format(
                    self.hpcConfig.get_value('user_name'),
                    self.hpcConfig.get_value('host'),
                    self.hpcConfig.get_value('execution_dir')))
            self.logger.debug('rsync output:\n{}'.format(rsync_output))
            # transfer job script
            rsync_output = rsync(
                "-azvrg", job_script, '{}@{}:{}'.format(
                    self.hpcConfig.get_value('user_name'),
                    self.hpcConfig.get_value('host'),
                    self.hpcConfig.get_value('execution_dir')))
            self.logger.debug('rsync output:\n{}'.format(rsync_output))

        except ErrorReturnCode as e:
            self.logger.error('Staging data failed:\n{}'.format(e.stderr))
            raise e


    def _collect_output(self, experiment):
        self._print_log('STDIN', experiment)
        self._print_log('STDERR', experiment)
        if experiment.is_vm_job():
            self._print_log('VTORQUE_DEBUG_LOG', experiment)


    def _clean_up(self):
        """Remove all files that are generated during the run."""
        raise NotImplementedError


    def cleanUp(self, jobID):
        assert jobID is not None
        path = self.get_value('path_vtorque_log') + "/" + jobID
        self.ssh_conn('rm', '-rf', path)


    def run_experiment(self, experimentCfg):
        self.logger.info("Experiment execution starts.")
        self.logger.info("Executing experiment '{}'".format(experimentCfg.name))
        # stage the input data
        self._stage_in_data(experimentCfg)
        # submit job
        self._submit_job(experimentCfg)
        # waiting for job until done
        self._wait_for_job(experimentCfg)
        # collect output
        self._collect_output(experimentCfg)
        # clean up
        #self.clean_up()
        # done
        self.logger.info('Experiment execution finished.')




