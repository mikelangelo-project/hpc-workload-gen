# CLI of the HPC-Workload-Generator

As first define the HPC back-end by the help of file [`hpc_backend.cfg`](doc/hpc_backend.cfg.md) and also your experiment configuration file [`experiment.yaml`](doc/experiment.yaml.md).

There are three mandatory arguments:
  * `-c` or `--config` HPC system configuration
  * `-e` or `--experiment` the experiment definition, see `experiment.yaml`](doc/experiment.yaml.md)
  * `-d` or `--data` the directory that contains your experiment's input data.


```
Usage: run.py [OPTIONS]

  Run workloads on specified systems.

Options:
  -e, --experiment FILENAME  the path to the workload.yaml  [required]
  -d, --data PATH            input data for the experiment  [required]
  -c, --config FILENAME      HPC configuration file, if not provided the default
                             is used. [./hpc_backend.cfg]
  --help                     Show this message and exit.
```
