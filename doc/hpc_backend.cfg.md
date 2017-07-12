# Configuration of the HPC-Workload-Generator

The configuration file needed for this project is auto-generated in case it is missing.  
To generate a new configuration file just run the program without further arguments:
```
run.py
```
This generates the default configuration `hpc_backend.cfg` in the present working directory.


```
{
    "domain": "",
    "grafana": true,
    "grafana_dashbord_name": "playground",
    "grafana_host": "localhost",
    "host": "localhost",
    "path_qsub": "/usr/bin/qsub",
    "path_qstat": "/usr/bin/qstat",
    "path_vsub": "/opt/vtorque/vsub",
    "poll_time_qstat": 5,
    "user_name": "user"
}
```

| Key                       | Value         | Default       | Description                                                                           |
| ---                       | :---:         | :---:         | :---:                                                                                 |
| domain                    | string        | -             | pbs uses this value and appends it for example the the job name                       |
| grafana                   | True / False  | True          | If you use vTorque with snap and a grafana/influxdb settup you can enable it here.    |
| grafana_dashbord_name     | string        | playground    | Grafana setting, this will be usesed to build the grafana link.                       |
| grafana_host              | string        | localhost     | host name of the grafana webfrontend.                                                 |
| host                      | string        | localhost     | host name of the pbs server. is useed for the ssh connection and the job id           |
| path_qsub                 | string        | /usr/bin/qsub     | location of the qsub binary on the frontend |
| path_qstat                | string        | /usr/bin/qstat    | location of the qstat binary on the frontend |
| path_vsub                 | string        | /opt/torque/vsub  | location of the vsub script on the frontend |
| poll_time_qstat           | int           | 5             | time between qstat calls during the job execution. [in sec]                           |
| user_name                 | string        | user          | user with ssh access to the pbs server and the rights to add jobs to the queue        |
