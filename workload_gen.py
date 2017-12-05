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
    hpcBackend.run_experiment(experimentCfg)
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
            "data" : { #TODO
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

