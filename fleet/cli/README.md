## FLEET
A command-line interface framework for launching HPC clusters.

### Usage
```bash
usage: fleet [-h] [-c CONFIG] [-nw NOWAIT] [-nr NOROLLBACK] [-u TEMPLATE_URL]
             [-t CLUSTER_TEMPLATE] [-p EXTRA_PARAMETERS] [-r REGION]
             {login,create,update,delete,start,stop,status,list,instances,configure,ssh,version}
             ...

fleet is a tool that can be used by IOOS modelers for HPC tasks

positional arguments:
  {login,create,update,delete,start,stop,status,list,instances,configure,ssh,version}
    login               Login with user credentials
    create              Creates an HPC fleet
    update              Updates an HPC fleet
    delete              Deletes an HPC fleet
    start               starts up an HPC fleet
    stop                stops an HPC fleet
    status              pull current status of the fleet
    list                display a list of stacks associated with fleet
    instances           display a list of all instances in a fleet
    configure           creating initial fleet configuration
    ssh                 Runs ssh to the master node, with username and ip
                        filled in based on the provided cluster
    version             display version of fleet

optional arguments:
  -h, --help            show this help message and exit
  -c CONFIG, --config CONFIG
                        specify an alternative configuration file
  -nw NOWAIT, --nowait NOWAIT
                        Do not wait for stack events
  -nr NOROLLBACK, --norollback NOROLLBACK
                        Disable stack rollback on an error
  -u TEMPLATE_URL, --template-url TEMPLATE_URL
                        Supply a URL for custom template
  -t CLUSTER_TEMPLATE, --cluster-template CLUSTER_TEMPLATE
                        Supply the filepath to a template
  -p EXTRA_PARAMETERS, --extra-parameters EXTRA_PARAMETERS
                        Supply extra parameters
  -r REGION, --region REGION
                        specify a specific region to connect to
```

A note to those developing: when installing using `$ python setup.py ...`,
make sure to use the ```develop``` optional command to make changes to your
code instantly available in the installed module.

### Portability
`fleet` is written in pure Python with an emphasis on being lightweight and platform-agnostic. This command line tool uses no external libraries, so all you need to use it is a working Python 3 interpreter.

### Configuration File(s)
In order to use `fleet`, you'll need a configuration file:

`.fleet.cfg` contains Cognito-specific information and is placed in the `/fleet/` directory:
    - pool_id
    - client_id
    - identity_pool_id
    - login
    - region

  You must obtain this information from an administrator (or your account, or something...).

  A sample `.fleet.sample.cfg` file is included in the project for layout reference.

__For Developers:__
1. `config.json` contains development application configuration settings for the
   simple Flask app used to test the CLI-API interaction workflow.
