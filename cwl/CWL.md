## Common Workflow Language for FLEET

The Common Workflow Language is designed to describe workflow. Essentially a data schema, CWL will dictate how users will be able to choose options from the FLEET command line tool (and potentially the web GUI). CWL documents are written in JSON or YAML, or sometimes a mix. It's important to note that the Common Language Workflow is *not* a piece of software, but rather a set of specifications to govern processes and make them easily shareable and understandable regardless of the platform they run the process on. In this sense, it's a bit like the WMS 1.3.0 specification for Web Mapping Service. 

The `.cwl` files will guide the command line tool by structuring allowable inputs. They will define a schema we can represent in a user interface, on the command line, and in a data object, all while maintaining its integrity from code to analysis of data.

### Goal

Using the [Common Workflow Language](https://www.commonwl.org) allows us to build out decoupled workflows which `fleet` can operate by. Instead of having hard dependencies for input files and messy logic checking existence of steps, we can execute different methods specified as options in the `fleet` command line tool without them interfering with each other. Processes which do not depend on each other will be able to run in parallel, and execution order is specified in the *workflow*, not the code. 

### Structure 

All CWL files are written in YAML syntax with key-value pairs. A sample workflow structure follows:

__Workflow file__

```
#!/usr/bin/env cwl-runner

cwlVersion: v1.0
class: Workflow
inputs:
  message: string
  infile : File

steps:
 
  print:
    run: test-echo.cwl
    in: 
      message: message
    out: []

  wrf:
    run: wrf-test.cwl
    in:
      file: infile
    out: []
outputs: []
```

What's going on here? Up top, we specify the version for the CWL, and the type of document this is (a workflow). Following this, we specify inputs; we declare the "type" (in context of CWL) of our inputs and the input name (this is similar to many programming languages, although here the order is reversed and they are separated by a colon).

Next, we list our workflow's steps. The steps can have any name we choose, but the specifications inside them are unique. For example, our first step is `print`; within this step, we declare what is going to be executed after the `run` keyword, followed by the name of another `.cwl` which will run. Next, we declare the inputs to that particular file. In this case, `test-echo.cwl` has an input of named `message`, and will search for that when invoked. Following inputs are outputs; here we output nothing, so we "return" an empty array.

The above logic applies to the final step, `wrf`, but instead of a message, `wrf-test.cwl` expects a file to be given. 

Finally, the workflow declares `outputs`, which are an empty array.

__Job file__

A *job file* is the vehicle by which parameters are passed to the Workflow file. In it, parameters are specified by name, their types declared, and any paths (and potentially more information?) needed to get to the parameters. All Job files are written in YAML syntax as well. Take a look at the sample file that pairs with the above Workflow:

```
message: This doesn't have to run sequentially...
infile:
  class: File
  path: wrf_test.sh 
```

The message is defined explicitly (it's just a string), where the `infile` has its type declared and path specified.


### Running the Workflow

To execute a Workflow, you'll need a `.cwl` engine. We currently use the `cwltool`, written in Python, which can be installed into your local Python environment by running 

```bash
pip install cwlref-runner
```

Running your workflow becomes as simple as invoking the `cwltool` and supplying the `.cwl` and `.yml` files to the command line:

```bash
cwl-runner workflow.cwl wrf-test.yml
```

__It should be noted__ that the Python `cwltool` is actually __not designed__ for production usage. Instead, we should use [Toil](https://toil.readthedocs.io/en/), also written in Python, or one of the [other implementations](https://www.commonwl.org/#Implementations). 

### Other Notes

__How will validation work, and how will it get to the front-end if CWL is not JSON?__

Currently, there is a JavaScript [library](https://www.npmjs.com/package/cwl-json-schema) that converts CWL to JSON.
