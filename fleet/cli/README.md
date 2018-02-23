fleet is a framework for launching HPC clusters.

    usage: fleet [-h] [--config CONFIG_FILE] [--region REGION] [--nowait]
                      {create,update,delete,status,list,instances,version}
                      ...

    fleet is the a tool to launch and manage a fleet.

    positional arguments:
      {create,update,stop,delete,status,list,instances}
        create              creates a cluster
        update              update a running cluster
        delete              delete a cluster
        status              pull the current status of the cluster
        list                display a list of stacks associated with cfncluster
        instances           display a list of all instances in a cluster
        version             display the version of cfncluster cli

    optional arguments:
      -h, --help            show this help message and exit

      ----

      -- This stuff actually isn't defined in our code yet --

      --config CONFIG_FILE, -c CONFIG_FILE
                            specify a alternative config file
      --region REGION, -r REGION
                            specify a specific region to connect to
      --nowait, -nw         do not wait for stack events, after executing stack
                            command

A note to those developing: when installing using ```python setup.py ...```,
make sure to use the ```develop``` optional command to make changes to your
code instantly available in the installed module. 
