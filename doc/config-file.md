# Configuration of the HPC-Workload-Generator

The configuration file needed for this project is auto-generated. To generate a new configuration file just run the program with some simple test:
```
run.py --workload test/workload.yml --datadir .
```
This generates the default configuration inside the project root.

`workload.cfg`
```
{
    "domain": "",
    "grafana": true,
    "grafana_dashbord_name": "playground",
    "grafana_host": "localhost",
    "host": "localhost",
    "path_qsub": "/bin/qsub",
    "path_qstat": "/bin/qstat",
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
| path_qsub                 | string        | /bin/qsub     | location of the qsub binary on the pbs server                                         |
| path_qstat                | string        | /bin/qstat    | location of the qstat binary on the pbs server                                        |
| poll_time_qstat           | int           | 5             | time between qstat calls during the job execution. [in sec]                           |
| user_name                 | string        | user          | user with ssh access to the pbs server and the rights to add jobs to the queue        |
