import io
import json
import jsonschema
import os
import subprocess
import sys
import tempfile # temporary file creation
from cwl2json import Converter
from jsonschema import Draft4Validator # latest fully supported validator
from yaml import dump, safe_load # to dump yaml to temporary file

class CWLHandler(object):
    """
    The CWLHandler writes CWL Job files from JSON strings, validates CWL files
    against their corresponding .cwl templates, and executes the `cwl-runner`
    via a subprocess call."""

    def __init__(self):
        pass

    @staticmethod
    def job_from_json(job_ipt, template_str): 
        """Write a temporary .yml Job file from a JSON string
        
        :param str job_ipt: string of JSON-formatted job inputs
        :param str template_str: template string to write to

        example of template_str

        message: <some message>
        file:
          class: File
          path: a_path"""

        # TODO we are writing to a path that may not exist?
        script_dir = os.path.join(os.getcwd(), 'scripts')

        job = json.loads(job_ipt)
        template = safe_load(template_str)
        # iterate through keys of the template; for the matching keys in job, 
        # we want to write the values in
        for field in template.keys():
            for inp, val in job.items():
                if inp == field: # if the key matches, we want to assign the appropriate fields
                    if isinstance(template[field], dict):
                        for k, v in job[inp].items():
                            if k in template[field].keys():
                                if k == 'path':
                                    v = os.path.join(script_dir, v) # reference an existing path on the API machine
                                template[field][k] = v # assign the appropriate value
                    else: # assuming it's a single key-value pair
                        template[field] = job[inp] # assign appropriate value
        # default_flow_style=False dumps it in YAML style (string)
        return dump(template, default_flow_style=False) # dump to a file (called in with context)

    @staticmethod
    def gen_template(fp):
        """Generate a YAML input template for a passed Workflow filepath. Uses
        the cwltool's built-in functionality to do this with a subprocess call.

        :param str fp: filepath to Workflow file
        :returns str"""

        result = subprocess.run([
                     'cwltool',
                     '--make-template',
                     os.path.abspath(fp)
                     ], stdout=subprocess.PIPE) # capture the stdout so we can use it
        # stdout is a bytes object, so we must decode to get string
        tmp_str = result.stdout.decode()
        return tmp_str

    @staticmethod
    def ro_inputs(_s):
        """When the cwltool generates an input template from a .cwl file, its
        output is a string, e.g.

        message: a_string  # type "string"
        infile:  # type "File" (optional)
            class: File
            path: a/file/path

        We want to use the comments noting the input is required/optional for
        the user. Neither pyyaml nor ruamel.yaml provide the functionality
        we need to get the requirements out, so we must do it from the strings.

        This method splits a .yml string into lines and creates a record of the
        required and optional inputs. Assumptions about the YAML strings:
          1. Only one level of indentation (like above)
          2. All YAML block strings begin with no indentation
          3. The type of an input is always inside double quotes
          4. The (optional) argument is always in parentheses

        :param str _s: YAML string
        """


        required = {}
        optional = {}
        s = _s.splitlines() # arrays of characters
        for l in s:
            ln = l[:] # get all the characters in the array
            if not ln.startswith(' '): # no space means key
                # get word before :
                _key = ln[:ln.find(':')] # find returns lowest index for char
                _i = ln.find('"') + 1 # index of beginning of type
                i_ = len(ln) - ln[::-1].find('"') # get ind of last ", subtract
                _type = ln[_i:i_-1] # slice the string just to this part
                if 'optional' in ln: # assign to appropriate record
                    optional[_key] = {'type': _type}
                else:
                    required[_key] = {'type': _type}
            continue # these are the indented level lines, info not needed
        return (required, optional)
            


    @staticmethod
    def invoke_cwl(cwl, job):
        """Use subprocess to invoke the cwl-runner and execute a workflow
           :param str cwl: path to .cwl file
           :param str job: path to job .yml file"""
       
        print('\nAbout to validate\n\n{}\n\nagainst\n\n{}\n'.format(job_json, cwl_json))

        subprocess.run([
                        'cwl-runner', 
                        #'--debug',
                        os.path.abspath(cwl), os.path.abspath(job)  # input the job .yml filepath
                       ])
            
    def validate(self, job_json, cwl_json):
        """Validate a CWL job against its .cwl file after converting them
           to JSON.

           Intercept exceptions thrown by jsonschema validator, log them.
           
           TODO Return the list (dict?) of exceptions.
    
           :param dict job_json: JOB .yml in JSON form
           :param dict cwl_json: CWL .cwl in JSON form"""

       # instantiate jsonschema validator and validate the job against .cwl
        v = Draft4Validator(cwl_json)
        if v.is_valid(job_json) == True:
            print('~~~ Successfully validated ~~~')
            return True, None
        else:
            errors = sorted(v.iter_errors(job_json), key=lambda err: err.absolute_schema_path)
            for err in errors: # TODO return these?
                print('---\nError validating JSON: {}\nPlease check your .cwl and .yml\n---'.format(err))
            return False, errors
