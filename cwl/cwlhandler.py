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

import pdb
#from pprint import pprint as print

class CWLHandler(object):
    """
    The CWLHandler takes passed parameters (command line options, flags,
    filepaths, etc) and writes temporary CWL Job files (.cwl files with 
    `class: CommandLineTool` in the header). These Job files supply a
    corresponding .cwl Workflow file (.cwl file with `class: Workflow` in the
    header) with parameters in the form and structure it expects. These two 
    files are then passed to the `cwltool` via a subprocess call."""

    # TODO define parameters for initialization and writing

    def __init__(self):
        pass

    def write_job(self):
        """Write a temporary .cwl Job file with the passed parameters
        """

        _test = {
                    'py_file': {
                        'class': 'File',
                        'path': '/home/dalton/total_water_prediction/fleet/cli/testme.py'
                     }
                }
        return dump(_test)#, encoding='utf-8') # dump as bytes
        #return yml_out

    def invoke_cwl(self):
        """Use subprocess to invoke the cwl-runner and execute a workflow
           :param """
        
        with tempfile.NamedTemporaryFile(mode='a') as job_yml: # open tempfile
            job_yml.write(self.write_job()) # will probably pass in paramaters here
            job_yml.seek(0) # rewind to beginning
        
            ## convert to JSON and validate before executing
            ## NOTE I don't think the JSON validation does not validate the 
            ## "position" argument in the cwl but I think the cwlrunner DOES tho

            #import pdb; pdb.set_trace()

            # safe load the yml files 
            cwl = safe_load(open('/home/dalton/total_water_prediction/cwl/workflows/wrf-test-cwl.cwl'))
            #job = safe_load(open('/home/dalton/total_water_prediction/cwl/workflows/invalid.yml'))
            job = safe_load(open('/home/dalton/total_water_prediction/cwl/workflows/wrf-test-input.yml'))
            conv = Converter()
            cwl_json = conv.convert(cwl)
            job_json = conv.convert(job)

            print('\nAbout to validate\n\n{}\n\nagainst\n\n{}\n'.format(job_json, cwl_json))

            # validate JSON
            if self.validate(job_json, cwl_json):
                subprocess.run([
                            'cwl-runner', 
                            #'cwl-runner', '--debug',
                            #'/home/dalton/total_water_prediction/cwl/workflows/wrf_workflow.cwl', 
                            #'/home/dalton/total_water_prediction/cwl/workflows/wrf-test.cwl',
                            '/home/dalton/total_water_prediction/cwl/workflows/wrf-test-cwl.cwl',
                            #os.path.abspath(job_yml.name)])  # input the job .yml filepath
                            #'/home/dalton/total_water_prediction/cwl/workflows/wrf-test.yml'])
                            '/home/dalton/total_water_prediction/cwl/workflows/wrf-test-input.yml'])
            else:
                sys.exit()

    def validate(self, job_json, cwl_json):
        """Intercept exceptions thrown by jsonschema.validate(), log them, 
           and superficially fix them so that the CWL will pass JSON
           validation. Return the list (dict?) of exceptions.
    
           :param dict job_json: JOB .yml converted to JSON
           :param dict cwl_json: CWL .cwl converted to JSON"""

        v = Draft4Validator(cwl_json)
        if v.is_valid(job_json) == True:
            print('~~~ Successfully validated ~~~')
            return True
        else:
            errors = sorted(v.iter_errors(job_json), key=lambda err: err.absolute_schema_path)
            for err in errors:
                print('---\nError validating JSON: {}\nPlease check your .cwl and .yml\n---'.format(err))
            return False

