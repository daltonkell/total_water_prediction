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
    def job_from_json(job_str, template_name): 
        """Write a temporary .yml Job file from a JSON string
        
        :param str job_str: string of JSON-formatted job inputs
        :param str template_name: name of corresponding template to write to"""

        # TODO we are writing to a path that may not exist?
        script_dir = os.path.join(os.getcwd(), 'scripts')

        job = json.loads(job_str) # turns to dict
        # load the corresponding YAML template NOTE will this call from an asbolute or relative path?
        template = safe_load(open('cwl/templates/jobs/{}'.format(template_name)))
        # iterate through keys of the template; for the matching keys in job, 
        # we want to write the values in 
        for field in template.keys():
            for inp, val in job.items():
                if inp == field: # if the key matches, we want to assign the appropriate fields
                    for k, v in job[inp].items():
                        if k in template[field].keys():
                            if k == 'path':
                                v = os.path.join(script_dir, v) # reference an existing path on the API machine
                            template[field][k] = v # assign the appropriate value
        # default_flow_style=False dumps it in YAML style
        return dump(template, default_flow_style=False) # dump to a file (called in with context)

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

