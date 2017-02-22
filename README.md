# HPC-Workload-Generator

This project is part of [MIKELANGELO](http://mikelangelo-project.eu) and is a middle-ware between Systems like [Jenkins](https://jenkins.io/) or [Gitlab CI](https://about.gitlab.com/gitlab-ci/) and an HPC System that works with [PBS Torque](http://www.adaptivecomputing.com/products/open-source/torque/).
The aim of this project is to give CI tools an API that can be used to interact with a HPC batch system like Torque or for MIKELANGELO [vTorque](https://github.com/mikelangelo-project/), to run HPC jobs as part of the CI tool chain.

## Table of contents

* [Getting Started](#Getting-Started)
* [Prerequisites](#Prerequisites)
* [Installing](#Installing)
* [Example](#Example)
* [License](#License)
* [Acknowledgements](#Acknowledgements)
* Additional Documentation
    * [Configuration File](#README.md)
    * [Workload.yaml](#README.md)
    * [CLI](#README.md)


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

Alternately you can use a virtual environment to install the requirements.

### Example

This example executes the simplest workload possible. It will `echo` the host name of the compute node behind torque to a log file. See the [job_script.sh](test/ecperiment01/job_script.sh)

To test your run, execute:

```
./run.py --workload test/workload.yml --datadir .
```

If it not work the first time, then you should check the `workload.cfg`, make sure the setting matches your setup and your configuration. For more infos see [Configuration File](doc/config-file.md).

## License

hpc-workload-gen is distributed under the Apache License 2.0 license.

## Acknowledgements

This project  has been conducted within the RIA [MIKELANGELO
project](https://www.mikelangelo-project.eu) (no.  645402), started in January
2015, and co-funded by the European Commission under the H2020-ICT- 07-2014:
Advanced Cloud Infrastructures and Services programme.
