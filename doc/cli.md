# CLI of the HPC-Workload-Generator

The CLI is used to interact with the program. After you have set all the parameters in the [`workload.cfg`](doc/config-file.md) and have build your test workload with the [`workload.yaml`](doc/workload.yaml.md) you are able to run the program.  
The two mandatory options you have to provide are `-w` or `--workload`, this will specify the path to the workload.yaml that will be used to run your job. The second mandatory option ist the `-d` or `--datadir` which is the path to the directory that *contains* your experiment. (Watch out, the containing directory, *not* the experiment directory)  
If you need to provide a different configuration file then the default one `workload.cfg` you can use the `-c` or `--configfile` option and give the path to the configuration file to the `run.py`

```
Usage: run.py [OPTIONS]

  Run workloads on specified systems.

Options:
  -w, --workload PATH        the path to the workload.yaml  [required]
  -d, --datadir PATH         base path containing the experiment  [required]
  -c, --configfile FILENAME  Configuration file, if not provided the default
                             is used. [./workload.cfg]
  --help                     Show this message and exit.
```
