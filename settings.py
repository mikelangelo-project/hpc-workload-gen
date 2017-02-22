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
import json
import logging


class Configuration(object):
    """Connect to the hpc system."""

    def __init__(self, path='workload.cfg'):
        """
        Default values for the generator.

        The host where the PBS-Torque installation is hosted:
        self.host = 'vsbase2'

        The path to the qsub tool on the remote host:
        self.path_qsub = '/opt/dev/vTorque/src/qsub'

        The path to the qstat tool on the remote host:
        self.path_qstat = '/opt/torque/current/server/bin/qstat'

        The name of the remote user. This is used to generate the
        grafana link if grafana is used:
        self.user_name = 'jenkins'
        """
        self.logger = self._get_logger()
        self.config_dict = self._get_config_dict(path)
        self.logger.debug('{}'.format(self.config_dict))
        try:
            self.host = self.config_dict['host']
            self.domain = self.config_dict['domain']
            self.user_name = self.config_dict['user_name']

            self.poll_time_qstat = self.config_dict['poll_time_qstat']

            self.path_qsub = self.config_dict['path_qsub']
            self.path_qstat = self.config_dict['path_qstat']

            self.grafana = self.config_dict['grafana']
            self.grafana_host = self.config_dict['grafana_host']
            self.grafana_dashbord_name = self.config_dict[
                'grafana_dashbord_name']

        except (KeyError):
            self.logger.warning(
                '\nCofnig file is missing keys. Backup your file, delete the'
                ' origin file and rerun. A new config file will be written.'
                ' Please modify this on.'
            )
            exit(1)

        # non changeable parameters
        self.grafana_base_string = str(
            'https://{}/dashboard/db/{}?'
            'panelId=1&'
            'fullscreen&'.format(self.grafana_host, self.grafana_dashbord_name)
        )

    def _get_logger(self):
        """Setup the global logger."""
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

    def _get_config_dict(self, path):
        try:
            with open(path, 'r') as data_file:
                config_dict = json.load(data_file)
        except (IOError):
            # file not found
            self.logger.info('No Config file found! Write a new one.')
            config_dict = self._get_default_dict()
            with open(path, 'w') as data_file:
                json.dump(
                    config_dict, data_file, sort_keys=True, indent=4)
        except (ValueError) as e:
            # display json errors
            self.logger.error(
                'something is wrong with the json file.\n{}'.format(e))
            exit(1)
        self.logger.debug(
            json.dumps(config_dict, sort_keys=True, indent=4)
        )
        return config_dict

    def _get_default_dict(self):
        return_dict = {
            'host': 'localhost',
            'domain': '-',
            'user_name': 'user',
            'poll_time_qstat': 5,
            'path_qsub': '/bin/qsub',
            'path_qstat': '/bin/qstat',
            'grafana': True,
            'grafana_host': 'localhost',
            'grafana_dashbord_name': 'playground'
        }
        return return_dict
