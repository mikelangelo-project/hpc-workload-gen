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

"""Package to hold classes for the ci."""

# @Author: Uwe Schilling, schilling@hlrs.de
# @COMPANY: HLRS, University of Stuttgart
# @Date: 2016-11-22


import logging
import yaml


class Workload(object):
    """Class for Workload configuration."""

    def __init__(self, yuml_file='workload.yml', datadir=''):
        """Initialize this Class."""
        self.logger = self.__get_logger()
        self.logger.debug('Initialize class')

        self.workload_YAML_file = yuml_file
        self.workload_dict = self.__pars_yuml()

        self.logger.info('testing workload_generator')
        self.__test_workload_generator()

        self.name = self.workload_dict['name']
        self.params = self.workload_dict['params']
        try:
            self.vtorque = self.workload_dict['vTorque']
        except KeyError:
            self.logger.info('no vTorque keys in yaml.')
            self.logger.debug('set self.vtorque to None')
            self.vtorque = None
        self.datadir = datadir

    def __get_logger(self):
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

    def __pars_yuml(self):
        """Parsing yuml provided by the CI."""
        self.logger.info('parsing yuml provided by the CI')
        self.logger.debug('using %s as path to yuml' % self.workload_YAML_file)

        with open(self.workload_YAML_file, 'r') as stream:

            try:
                yuml_dict = yaml.load(stream)
                self.logger.debug('got directory form YAML: %s' % yuml_dict)
                # encode the structure of the real workload
                workload_dict = yuml_dict["workload"]
                return workload_dict

            except yaml.YAMLError as exc:
                self.logger.error(
                    'Could not read YAML file %s\n'
                    'content of the file:\n'
                    '%s\n'
                    'error is\n'
                    '%s' % (self.workload_YAML_file, stream, exc))
                self.logger.error('Without YAML no configuration, exiting')
                exit(1)

    def __test_workload_generator(self):
        """Test if structure of the yuml file is correct."""
        """
        Expected structure for workload_generator:
        workload:
            name: <workload name> [mandatory]
            params:
                job_script_name: <name> [mandatory]
                experiment_dir: <path> [mandatory] -> contains job_script
                qsub_number_of_nodes: <count> [optional]
                qsub_number_of_processes_per_node: <count> [optional]
            vTorque:
                IMG: <path to image e.g. /image/image.img>
                DISTRO: <debian|rethat|osv>
                RAM: <count>
                VCPUS: <count>
                VMS_PER_NODE: <count>
                METADATA <path>
                DISK <path>
                ARCH <x86_64>
                HYPERVISOR <kvm|skvm>
                VCPU_PINNING <true|false>
                VM_PROLOGUE <path>
                VM_EPILOGUE <path>
                VRDMA <true|false>
                IOCM <true|false>
                IOCM_MIN <count>
                IOCM_MAX <count>
                FS_TYPE <>
        """
        try:
            self.workload_dict['name']
            self.workload_dict['params']['job_script_name']
            self.workload_dict['params']['experiment_dir']

        except KeyError:
            self.logger.error(
                'Mandatory things missing in workload_generator:\n'
                'workload[name]: %s\n'
                'workload[params][job_script_name]: %s\n'
                'workload[params][experiment_dir]: %s\n' % (
                    self.workload_dict['name'],
                    self.workload_dict['params']['job_script_name'],
                    self.workload_dict['params']['experiment_dir']))
            self.logger.error('workload_generator error, exiting')
            exit(1)

        try:
            # the parameters are optional
            if not isinstance(
                    self.workload_dict['params']
                    ['qsub_number_of_nodes'], int):
                self.logger.error(
                    'workload[params][qsub_number_of_nodes]'
                    'is not an integer: %s'
                    % self.workload_dict['params']['qsub_number_of_nodes'])

            if not isinstance(
                    self.workload_dict['params']
                    ['qsub_number_of_processes_per_node'], int):
                self.logger.error(
                    'workload[params][qsub_number_of_processes_per_node]'
                    'is not an integer: %s' %
                    self.workload_generator['params']
                    ['qsub_number_of_processes_per_node'])

        except KeyError:
            self.logger.warning('no qsub additions')

        # test if files exist
        '''
        # TODO test if job_script_dir_path exist

        # test if job script exist
        job_script_path = job_script_dir_path + '/job_script.sh'
        if not os.path.isfile(job_script_path):
            logger.error('Job script dose not exist! %s' % job_script_path)
            exit(1)
        '''

    def get_name(self):
        """Getter for name."""
        self.logger.debug('returning name %s' % self.name)
        return self.name

    def get_params(self, param):
        """Getter for parameters."""
        try:
            self.logger.debug(
                'returning parameters %s' % self.params[str(param)])
            return self.params[str(param)]
        except KeyError:
            self.logger.info('no parameter %s' % param)
            self.logger.debug('returning None')
            return None

    def get_vtorque(self):
        """Getter for vTorque stuff."""
        try:
            self.logger.debug('returning vTorque stuff %s' % self.vtorque)
            return self.vtorque
        except KeyError:
            self.logger.info('no parameter for vTorque stuff')
            self.logger.debug('returning None')
            return None

    def get_data_dir(self):
        """Getter for base directory."""
        return_str = self.datadir + self.get_params('experiment_dir')
        self.logger.debug('returning data directory: %s' % return_str)
        return return_str
