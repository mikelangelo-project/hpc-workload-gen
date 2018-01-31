# HPC-Workload-Generator

This project is part of [MIKELANGELO](http://mikelangelo-project.eu) and is a middle-ware between Systems like [Jenkins](https://jenkins.io/) or [Gitlab CI](https://about.gitlab.com/gitlab-ci/) and an HPC System that works with [PBS Torque](http://www.adaptivecomputing.com/products/open-source/torque/) or [vTorque](https://github.com/mikelangelo-project/vTorque).
The aim of this project is to give CI tools an API that can be used to interact with a HPC batch system like Torque or for MIKELANGELO [vTorque](https://github.com/mikelangelo-project/), to run HPC jobs as part of the CI tool chain.

## Table of contents

* [Getting Started](#getting-started)
* [Prerequisites](#prerequisites)
* [Installing](#installing)
* [Example](#example)
* [License](#license)
* [Acknowledgement](#acknowledgement)
* Additional Documentation
    * [HPC Back-end Configuration](doc/config-file.md)
    * [Experiment Configuration](doc/experiment.yaml.md)
    * [CLI](doc/cli.md)


## Getting Started

These instructions will get you a copy of the project up and running on your local machine for development and testing purposes. See deployment for notes on how to deploy the project on a live system.

### Prerequisites

The project is written in Python and needs a Python installation on your local machine. Further, packages form PIP are required. Please install both to have the environment you need to develop / test / run this project.

```
For Ubuntu 16.10

sudo apt install python2.7
sudo apt install python-pip
```

For submitting the job to a torque installation you need `ssh` access to the remote system. Please make sure that you can access this machine without a password (key access).

You can test this by running:
```
ssh user_name@host.domain 'hostname'
```
`user_name` your login name.  
`host` the host with pbs server installed (`qsub` / `qstat` should be installed there).  
`domain` the domain of your host.  

You have to put this variables into the configuration file after the configuration file is generated.

### Installing

First, clone or fork the project:

```
git clone https://github.com/mikelangelo-project/hpc-workload-gen.git
```

Second, install the dependency:


```
# Global for all users:
sudo -H pip install -r requirements.txt
```

```
# One user:
pip install -r requirements.txt
```

And as a final step create an environments file with the following variables. Those will be applied during runtime. This way credentials and code are clearly separated.

| Environment Varaible       | Type               | Description                    |
| :---                       | :---               | :---                           |
| domain                     | string             | Your TLD                       |
| host                       | string             | HPC front-end                  |
| user_name                  | string             | HPC user                       |
| ssh_port                   | integer            | SSH port of HPC front-end      |
| ssh_key                    | string             | SSH key for HPC front-end      |
| grafana                    | boolean            | Grafana dashboard available    |
| grafana_host               | string             | Grafana host                   |
| grafana_dashborad_name     | string             | Grafana dashboard name         |
| grafana_dashboard_url      | string             | Grafana dashboard URL          |
| path_qstat                 | string             | Path to `qstat` on HPC system  |
| path_qsub                  | string             | Path to `qsub` on HPC system   |
| path_vsub                  | string             | Path to `vsub` on HPC system   |
| path_vtorque_log           | string             | Path to vTorque log            |
| execution_dir              | string             | Path to job execution dir      |
| poll_time_qstat            | integer            | Time to check job status       |
| log_file                   | string             | Path to log file               |
| log_level_file             | string             | Log level for log file         |
| log_level_console          | string             | Log level for stdout/console   |

You can it either add to the CI user's `~/.bashrc` or as a system-wide solution, place it in /etc/profile.d/scotty_ci.sh
Mind to make environment variables persistent by the help of `export variable=value`.

Alternately you can use a virtual environment to install the requirements.

### Example

This example executes the simplest workload possible. It will `echo` the host name of the compute node behind torque to a log file. See the [job_script.sh](test/experiment01/job_script.sh)

To test your run, execute:

```
./run.py --experiment test/workload.yml --data .
```

If it not work the first time, then you should check the `hpc_backend.cfg`, make sure the setting matches your setup and your configuration. For more infos see [Configuration File](doc/config-file.md).

## License

This project is distributed under the Apache License 2.0 license.

## Acknowledgement

This project  has been conducted within the RIA [MIKELANGELO project](https://www.mikelangelo-project.eu) (no.  645402), started in January 2015, and co-funded by the European Commission under the H2020-ICT- 07-2014: Advanced Cloud Infrastructures and Services programme.
