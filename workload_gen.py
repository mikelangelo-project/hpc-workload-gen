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

"""HPC Workload Generator for Scotty CI."""

# @Author: Nico Struckmann, struckmann@hlrs.de
# @COMPANY: HLRS, University of Stuttgart
# @Date: 2018-01-31
import logging

from scotty import utils

from api.experiment_config import ExperimentConfig
from api.hpc_backend import HPCBackend


logger = logging.getLogger(__name__)
hpcBackend = None
jobID = None



def run(context):
    workloadDef = context.v1.workload
    # logging
    logger.info("HPC workload generator '{}' starting.".format(workloadDef.name))
    # get the helper
    exp_helper = utils.ExperimentHelper(context)
    # initialize experiment configuration
    experimentCfg = ExperimentConfig(workloadDef)
    # initialize HPC back-end connection handler
    hpcConfig = experimentCfg.getHPCConfig()
    hpcBackend = HPCBackend(hpcConfig)
    # execute the experiment
    try:
        hpcBackend.run_experiment(experimentCfg)
    except Exception as e:
        logger.error(e)
        # downwards compatibility, thus try/catch if not implemented
        try:
            workloadDef.failed()
        except Exception as ex:
            pass
        return None;
    # cache jobID for clean up
    jobID = experimentCfg.get_job_id();
    # construct result paths
    stdoutPath = hpcConfig.get_value('execution_dir') + experimentCfg.get_job_script() + 'o' + experimentCfg.get_stripped_job_id()
    stdErrPath = hpcConfig.get_value('execution_dir') + experimentCfg.get_job_script() + 'e' + experimentCfg.get_stripped_job_id()
    vtorque_log = hpcConfig.get_value('path_vtorque_log') + "/" + experimentCfg.get_job_id() + "debug.log"
    # return results
    return {
            "endpoint" : {
               "identifier": "submission host",
               "host" : hpcConfig.get_value('host')
            },
            "data" : {
                "stdout" : stdoutPath,
                "stderr" : stdErrPath,
                "vtorque_log" : vtorque_log
            },
            "config" : experimentCfg,
            "backend" : "HPC"
        }


def clean(context):
    if hpcBackend is not None:
        hpcBackend.cleanUp(jobID)

