

from __future__ import with_statement
import sys
import json
import yaml
import os
import re

from api.logger import getLogger
from api.hpc_config import HPCBackendConfiguration


class ExperimentConfig(object):
    """Class for experiment configuration."""

    def __init__(self, workloadDef):
        """Initialize this Class."""
        self.name = None
        # experiment artefacts
        self.job_script = None
        self.input_data = None
        self.qsub_args = None
        self.vsub_args = None
        # hpc backend config
        self.hpc_config = None
        # set during execution
        self.job_id = None
        self.stripped_job_id = None
        self.start_time = None
        self.stop_time = None
        self.job_state = None
        # logging
        self.logger = getLogger(__name__)
        self.logger.debug('Initialize class')
        # parse and validate experiments
        self.__load_experiment(workloadDef)


    def __load_experiment(self, experimentCfg):
        """Validate experiment's YAML, parsed/provided by scotty."""
        
        """
        Expected structure for experiment configuration:
        experiment:
            name: <experiment name> [mandatory]
            params:
              job_script: example/experiment01/job_script.sh  [mandatory]
              input_data: example/experiment01/input_data/    [optional]
              hpc_config: example/hpc_backend.cfg             [optional]
              qsub_args: "-l nodes=1:debug                    [optional]
              vsub_args: "-vm vcpus=4 -vm ram=8012M"          [optional]
        """
        
        self.logger.debug('Validating experiment configuration')
        
        try:
            # mandatory parameters
            experimentCfg.name
            experimentCfg.params['job_script']

            #experimentCfg.params['application_log']
            self.logger.debug('All mandatory parameters found:\n{}'.format(
                json.dumps(experimentCfg.params, sort_keys=False, indent=4)))
        except KeyError as e:
            self.logger.error(
                'Mandatory parameter \'{}\' is missing.'.format(e.args[0])
            )
            sys.exit(1)
        
        # apply values
        self.name = experimentCfg.name
        self.job_script = self.unifyPath(experimentCfg.params['job_script'])


        # create remote paths
        #experiment['remote'] = {}
        #experiment['remote']['experiment_dir'] = os.path.basename(experiment['params']['experiment_dir'])
        #experiment['remote']['job_script'] = os.path.basename(experiment['params']['job_script'])
        
        # check if the experiment data path is relative or absolute
        #if not os.path.isabs(experiment['experiment_dir']):
        #    newPath = os.getcwd() + '/' + self.experiment['experiment_dir']
        #    if os.path.isdir(newPath):
        #        self.experiment['experiment_dir'] = newPath
        #    else:
        #        self.logger.error("Experiment directory '{}' defined in the experiment YAML configuration file '{}' cannot be found.".format(self.experiment['experiment_dir'], experimentCfg))
        #        sys.exit(1)


        #
        # optional params
        #
        
        if 'qsub_args' in experimentCfg.params:
            self.qsub_args = experimentCfg.params['qsub_args']

        if 'vsub_args' in experimentCfg.params:
            self.vsub_args = experimentCfg.params['vsub_args']

        if 'input_data' in experimentCfg.params:
            self.input_data = self.unifyPath(experimentCfg.params['input_data'])

        if "hpc_config" in experimentCfg.params:
            hpcConfigPath = self.unifyPath(experimentCfg.params['hpc_config'])
        else:
            # default file is picked
            hpcConfigPath = self.unifyPath("./example/hpc_backend.cfg")
        self.hpc_config = HPCBackendConfiguration(hpcConfigPath)


    def unifyPath(self, path):
        if path is None:
            self.logger.error("No path is given to unify it.")
            sys.exit(1)
        elif not os.path.isabs(path):
            newPath = os.getcwd() + '/' + path
            if os.path.isabs(newPath):
                return newPath
            else:
                self.logger.error(
                    "Path '{}' defined in the experiment YAML cannot be found."
                    .format(newPath))
                sys.exit(1)
        return path


    def getHPCConfig(self):
        return self.hpc_config


    def get_name(self):
        """Getter for name."""
        return self.name


    def is_vm_job(self):
        """Getter for vTorque args."""
        self.logger.debug('vTorque arguments: {}'.format(json.dumps(self.vsub_args)))
        return self.vsub_args is not None


    def get_job_script(self):
        return self.job_script


    def get_input_data(self):
        return self.input_data


    def get_vsub_args(self):
        return self.vsub_args


    def get_qsub_args(self):
        return self.qsub_args


    def set_job_id(self, jobID):
        if self.job_id is not None:
            raise Exception("Job ID cannot be overridden")
        self.job_id = jobID
        self.stripped_job_id = re.findall('^\d+',jobID)[0]


    def get_job_id(self):
        return self.job_id


    def get_stripped_job_id(self):
        return self.stripped_job_id


    def set_start_time(self, startTime):
        if self.job_id is not None:
            raise Exception("Job ID cannot be overridden")
        self.start_time = startTime


    def get_start_time(self):
        return self.start_time


    def set_end_time(self, startTime):
        if self.job_id is not None:
            raise Exception("Job ID cannot be overridden")
        self.end_time = startTime


    def get_end_time(self):
        return self.end_time


    def set_job_state(self, jobState):
        if self.job_state is not None:
            raise Exception("Job ID cannot be overridden")
        self.job_state = jobState


    def get_job_state(self):
        return self.job_state
