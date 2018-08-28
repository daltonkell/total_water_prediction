## Common Workflow Language for FLEET

The Common Workflow Language is designed to describe workflow. Essentially a data schema, CWL will dictate how users will be able to choose options from the FLEET command line tool (and potentially the web GUI). CWL documents are written in JSON or YAML, or sometimes a mix. It's important to note that the Common Language Workflow is *not* a piece of software, but rather a set of specifications to govern processes and make them easily shareable and understandable regardless of the platform they run the process on. In this sense, it's a bit like the WMS 1.3.0 specification for Web Mapping Service. 

The `.cwl` files will guide the command line tool by structuring allowable inputs. They will define a schema we can represent in a user interface, on the command line, and in a data object, all while maintaining its integrity from code to analysis of data.

### Goal

We want to separate the command line interface processes from the service which those processes facilitate. For instance, if a user calls on the command line tool to execute a model run, the command line tool that responds to that call should assume that all of the needed information to execute a model run is available to use. This CWL will help ensure that those materials are available and ready before thatcommand is actually needed. So we have something like this:


--- 
__WHAT I DON'T UNDERSTAND__

- Where are the examples? 
- Am I supposed to leverage the existing `cwltool` for my command line tool, or write my own?
- Where can I find the reference for what fields I can enter into a `.cwl` file, or the corresponding `.yml` or `.json` files?


### Outlining the Specification

Begin with two aspects of the modeling workflow: 
- Input Data 
- Execution

### Execute

The `execute` service is designed to allow users to execute operations (whether they are launching a cluster to begin computation, stopping a cluster, allocating more resources to a cluster/taking resources away, etc.). 

__What do we need for execution?__

In order to successfully execute, AWS EC2 would need to have:
- binary model (compiled code)
- cluster specification information
- number of model runs to execute 

The `execute` call (or some other method) would then send this information to the EC2 servers to begin execution

The actual execution step would then consist of the server(s) running the model. Basic output should include:
- system logs
- status (completion percentage, warnings, possibly cost/usage?)

- Users would have to be able to submit information via the CLI and ensure it reaches the AWS service reliably, accruately, and securely
- JSON strings seem perfect for this as they translate super well over HTTP and HTTPS connections

### Input Data 

The input option for our tool is not a service to *upload data*, but rather to input the needed information needed to execute model runs in the cloud. A potential workflow follows:
- upload a small configuration file containing the necessary information stated above 
- enter the information in a piece-wise fashion, and then assimilate the information into a common structure (probably JSON schema); this structure could be another intermediate step, or could be directly interpretable by the EC2 service
- verify all the needed information is present in the structure and is of valid types

This verification step is precisely the reason why we need a schema which is easily validated. While the CWL documentation shows that most `.cwl` files are written in `.yml`, YAML isn't necessarily easy to validate. JSON, however, *is* easy.

*Important Note about JSON Schemas*

```
The $schema keyword is used to declare that a JSON fragment is actually a piece of JSON Schema. It also declares which version of the JSON Schema standard that the schema was written against.

It is recommended that all JSON Schemas have a $schema entry, which must be at the root. Therefore most of the time, you’ll want this at the root of your schema:

"$schema": "http://json-schema.org/schema#"
```

We could get seriously crazy strict and specific with the JSON schema, but for now it's appropriate to have just basic field types and expected values. 

__How will validation work, and how will it get to the front-end if CWL is not JSON?__

Currently, there is a JavaScript [library](https://www.npmjs.com/package/cwl-json-schema) that converts CWL to JSON.

__Why not just use JSON and make our own parser?__

I'm struggling with this right now, but because CWL has its own Python parser, it's worth a shot. We can declare the types and expected values of the fields in CWL, and the JS library will parse them out. Now to design a couple CWL schemas for input and executiion. 

