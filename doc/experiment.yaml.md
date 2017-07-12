# experiment.yaml of the HPC-Workload-Generator

An experiment is in this terminology an application the is executed with different parameters with different amounts of resources in order to gain a deeper insight in the application characteristics and scaling behavior.

## Experiment

The file `experiment.yaml` is used to specify on more experiments to be executed on an HPC system.  
As the name suggests, this yaml file specifies an experiment. Supported HPC batch system resource manager is [vTorque](https://github.com/mikelangelo-project/vTorque), thus also Torque.

### Experiment Configuration

Expected structure for an `experiment.yaml` file:

```
experiment:
    name: <workload name> [mandatory]
    generator: <name of the workload generator> [mandatory] hpc-workload-gen | ...
    params:
        job_script: <name> [mandatory]
        experiment_dir: <path> [mandatory] -> contains job_script and inout data
        qsub_args: <string> [optional]
    vTorque:
        img: <name of guest image to use>
        distro: <debian|rethat|osv>
        ram: <count>
        vcpus: <count>
        vms_per_node: <count>
        metadata: <path>
        disk: <path>
        arch: <x86_64>
        vcpu_pinning: <true|false|pinning_file>
        vm_prologue: <path>
        vm_epilogue: <path>
        vrdma: <true|false>
        iocm: <true|false>
        iocm_min_cores: <count>
        iocm_max_cores: <count>
        fstype: <ramdisk|sharedfs>
```

## Example

Create an experiment directory where you place your job script and the application binaries and other file related to the experiment you want to run. 

Then create the experiment configuration file, for example called `experiment.yaml`

```
- experiment:
    name: hpc-workload-gen
    generator: hpc-workload-gen
    params:
      job_script: experiment01/job_script.sh
      experiment_dir: experiment01
      qsub_args: "-l nodes=2:ppn=16"
- experiment:
    name: hpc-workload-gen
    generator: hpc-workload-gen
    params:
      job_script: experiment01/job_script.sh
      experiment_dir: experiment01
      qsub_args: "-l nodes=4:ppn=16"
- experiment:
    ...
```
Your experiments directory structure may look similar to this.

```
.
├── experiment01/
│   ├── data/
│   ├── bin/
│   └── job_script.sh
└── experiment.yaml
```