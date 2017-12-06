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

"""Configuration class Object."""

# @Author: Uwe Schilling, schilling@hlrs.de
# @COMPANY: HLRS, University of Stuttgart
# @Date: 2017-02-21

from __future__ import with_statement
import sys
import json
import os
from api.logger import getLogger


class HPCBackendConfiguration(object):
    """Connect to the hpc system."""


    def __init__(self, hpcConfigPath):
        """
        Default values for the generator.

        The host where the PBS-Torque installation is hosted:
        self.host = 'vsbase2'

        The path to the qsub tool on the remote host:
        self.path_qsub = '/usr/bin/qstat'

        The path to the vsub tool on the remote host:
        self.path_vsub = '/opt/vtorque/vsub'

        The path to the qstat tool on the remote host:
        self.path_qstat = '/usr/bin/qstat'

        The name of the remote user. This is used to generate the
        grafana link if grafana is used:
        self.user_name = 'jenkins'
        """
        self.logger = getLogger(__name__)

        # ensure file exists
        if hpcConfigPath is None or not os.path.isfile(hpcConfigPath):
            self.logger.error(
                'HPC back-end configuration \'{}\' is missing.'.format(hpcConfigPath)
            )
            sys.exit(1)

        #
        # replace placeholders with settings from env vars
        #
        varList = [
            'domain', 'host', 'user_name', 'ssh_port', 'ssh_key',
            'grafana', 'grafana_dashbord_name', 'grafana_host',
            'path_qstat', 'path_qsub', 'path_vsub', 'path_vtorque_log',
            'execution_dir', 'poll_time_qstat']
        # Read in the file
        with open(hpcConfigPath, 'r') as file :
            fileContent = file.read()
        # Replace the target string
        for key in varList:
          fileContent = fileContent.replace('__'+key+'__', os.environ[key])
        # Write the file out again
        with open(hpcConfigPath, 'w') as file:
            file.write(fileContent)

        # load JSON
        self.config_dict = self._get_config_dict(hpcConfigPath)
        self.logger.debug('{}'.format(self.config_dict))
        try:
            self.host = self.config_dict['host']
            self.domain = self.config_dict['domain']
            self.user_name = self.config_dict['user_name']
            self.execution_dir = self.config_dict['execution_dir']

            self.poll_time_qstat = self.config_dict['poll_time_qstat']

            self.path_qsub = self.config_dict['path_qsub']
            self.path_vsub = self.config_dict['path_vsub']
            self.path_qstat = self.config_dict['path_qstat']
            self.path_vtorque_log = self.config_dict['path_vtorque_log']

            self.grafana = self.config_dict['grafana']
            self.grafana_host = self.config_dict['grafana_host']
            self.grafana_dashbord_name = self.config_dict['grafana_dashbord_name']

            self.grafana_base_string = str(
                self.config_dict['grafana_dashbord_url'].format(self.grafana_host, self.grafana_dashbord_name)
            )

        except (KeyError) as e:
            self.logger.warning(
                '\nConfig file \'{}\'is missing key \'{}\''
            )
            sys.exit(1)


    def _get_config_dict(self, path):
        try:
            with open(path, 'r') as data_file:
                config_dict = json.load(data_file)
        except (IOError):
            # file not found
            self.logger.info('No HPC backend configuration found!')
            config_dict = self._get_default_dict()
            with open(path, 'w') as data_file:
                json.dump(
                    config_dict, data_file, sort_keys=True, indent=4)
            self.logger.info('New HPC backend configuration file \'{}\' created.\nPlease edit it and re-run.'.format(path))
            sys.exit(1);
        except (ValueError) as e:
            # display json errors
            self.logger.error(
                'something is wrong with the json file.\n{}'.format(e))
            sys.exit(1)
        self.logger.debug(
            json.dumps(config_dict, sort_keys=True, indent=4)
        )
        return config_dict


    def _get_default_dict(self):
        return_dict = {
            'host': 'submission-frontend',
            'domain': 'mydomain',
            'user_name': 'ci',
            'poll_time_qstat': 5,
            'execution_dir': './',
            'path_qsub': '/usr/bin/qsub',
            'path_qstat': '/usr/bin/qstat',
            'path_vsub': '/opt/vtorque/vsub',
            'grafana': True,
            'grafana_host': 'localhost',
            'grafana_dashbord_name': 'playground'
        }
        return return_dict


    def get_value(self, key):
        #TODO use consts for keys
        return self.config_dict[key]



