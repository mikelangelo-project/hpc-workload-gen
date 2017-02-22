# workload.yaml of the HPC-Workload-Generator

The `workload.yaml` is used to specify a experiment and can be created and edited by a user of the CI tool. Only the experiment repo has a real workload definition inside the `experiment.yaml` - the workload-generator has only a `test/workload.yaml` for testing.

## Experiment

An experiment is a execution of an application through the CI within an infrastructure. As the name (hpc-workload-gen) suggests, this yaml file specifies an workload for an HPC system (PBS Torque / vTorque).  

### yaml parameters

Expected structure for the `workload.yaml`:

```
workload:
    name: <workload name> [mandatory]
    generator: <name of the workload generator> [mandatory] hpc-workload-gen | ...
    params:
        job_script_name: <name> [mandatory]
        experiment_dir: <path> [mandatory] -> contains job_script
        qsub_number_of_nodes: <count> [optional]
        qsub_number_of_processes_per_node: <count> [optional]
        application_log: <file> [mandatory] -> single log-file
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
```

## Example

A full example, this will give you (as user) an overview how to specify your experiment. First create a `workload.yaml`:  
The user create an experiment in the experiment repo like experiment/hpc. Inside this repo must be an `experiment.yaml`. This `experiment.yaml` has one or more workload definitions like:

```
- workload:
    name: hpc-workload-gen
    generator: hpc-workload-gen
    params:
      job_script_name: job_script.sh
      experiment_dir: experiment01
      qsub_number_of_nodes: 1
      qsub_number_of_processes_per_node: 16
      application_log: ~/experiment_log/log
```

* With this your job will be executed on 1 node with 16 processes. This will be handled by PBS torque / vTorque.
* The script that will be executed on the remote node is `experiment01/job_script` the log-file of your job should be written (or moved) to `~/experiment_log/log` so the workload generator can show you the informations.
* your file structure should look something like this:

```
.
├── experiment01
│   └── job_script.sh
└── workload.yml
```

## CI configuration

Depending on the tool used, this differs. But the basic work-flow should be:

* check out user experiment
* phars yaml file for the name (workload gen name)
* checkout the matching worklod generator
* run the `run.py` whit the cli
