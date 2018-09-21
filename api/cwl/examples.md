## Annotated Examples of CWL `CommandLineTool` and `Workflow Files`

__tar-param.cwl__

```
#!/usr/bin/env cwl-runner

cwlVersion: v1.0
class: CommandLineTool
baseCommand: [tar, xf]             # programs to be run once invoked (in order)
inputs:                            # list all inputs
  tarfile:                         # first input name: tarfile
    type: File                     # type of the input -- this input is a File (an actual object, requires a path)
    inputBinding:                  # inputBinding describes how the input should appear on the command line 
      position: 1                  #   -- this expects first position
  extractfile:                     # second input name: extractfile
    type: string                   # this input expects a string 
    inputBinding:                  #   again, inputBinding describes how input should appear 
      position: 2                  #   -- at the second value on the command line
outputs:                           # just like we declare inputs, also can declare expected outputs
  example_out:                     # first output name: example_out
    type: File                     # output is expected to be an object
    outputBinding:                 # outputBinding describes how to set the value of each output parameter
      glob: $(inputs.extractfile)  # here we get the desired file by specifying the path of where it's located
                                   #   -- since extractfile is a string (i.e. name.txt), we can use this to glob the filename
```

__tar-param-job.yml__

```
tarfile:                  # input name matches the expected first input of tar-param.cwl
  class: File             # instead of using 'type' here, we use 'class' (not really sure why)
  path: hello.tar         # specifying the actual path of the input (how it appears on the machine)
extractfile: goodbye.txt  # second input name, matches the input name of the second expected input
                          # instead of nesting the type or value, because this is a string, it seems we can just insert it
```

__arguments.cwl__

```
#!/usr/bin/env cwl-runner

cwlVersion: v1.0
class: CommandLineTool
label: Example trivial wrapper for Java 9 compiler
hints:
  DockerRequirement:
    dockerPull: openjdk:9.0.1-11-slim
baseCommand: javac                      # command to be invoked
arguments: ["-d", $(runtime.outdir)]    # supplying additional args to command line that don't necessarily require input values
inputs:                                 # listing inputs
  src:                                  # first input name: src
    type: File                          # expects an object
    inputBinding:                       
      position: 1                       # expected src as the first input on the command line
outputs:                                # listing outputs
  classfile:                            # first expected output name: classfile
    type: File                          # expects an object
    outputBinding:                      # how to set the value of the output parameter
      glob: "*.class"                   #   -- in this case we glob whatever files have the .class extension
```

__arguments-job.yml__

```
src:                 # first input name matches first expected input name
  class: File        # declare the input is a File object
  path: Hello.java   # path on the machine
```

Next, we see an example of a `Workflow` file which will connect `tar-param.cwl` and `arguments.cwl`.
