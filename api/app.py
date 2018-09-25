import json
import boto3
from warrant.aws_srp import AWSSRP # warrant for AWS Cognito authentication
from warrant.exceptions import ForceChangePasswordException
import os
import subprocess
import sys
from cwl import CWLHandler
from cwl2json import Converter
from datetime import datetime
from flask import Flask, request, jsonify, Response, redirect, url_for
from tempfile import NamedTemporaryFile, TemporaryDirectory
from verify import Verify
from yaml import safe_load, dump

# instantiate the application
app = Flask(__name__)

# configuration--load up the config file
conf = json.load(open('config.json'))

# -------------------------------------------------------
# GLOBAL DICT FOR STORING USER INFORMATION, REQUESTS, ETC
# -------------------------------------------------------
"""
Instead of using a session directly to store state between user requests and
responses from the CLI, we're going to simplify the process since this is not
theh final API construction. Instead of a database, we're going to use a simple
global dict to create key-value pairs for users that log in with their JWT. 
Within these key-value pairs will be more dicts, storing information about a 
current request for a CWL run. Once that CWL run executes or fails, we delete
that key from the dict; this will help manage memory. Note that every time the
app is restarted this pseudo-database is blown away, which is entirely 
inefficient for any type of production environment.
"""

gstor = {}

verifier = Verify() # token verifier

# Method to verify user
def verify(token):
    """Verify a token and return claims

    :param str token: JSON Web Token string"""

    client_id = conf['client_id']
    keys_url = conf['keys_url']
    return verifier.verify_token(token, keys_url, client_id)

#-------
# ROUTES
# ------

@app.route('/list', methods=['GET'])
def list_clusters():
    """List all clusters. If the passed request headers contain the stack name,
    list the stacks with the specified name"""

    if not request.method == 'GET':
        return Response(response='Please provide a GET request', status=400)
    if request.headers.get('stack_name'):
        sn = request.headers.get('stack_name')
        resp = {'stack1{}'.format(sn): 'clusterXYZ'}
    else:
        resp = ['cluster1, cluster2, cluster3']
    return jsonify(status=resp)

@app.route('/create-and-update', methods=['GET', 'POST'])
def create_update():
    """Create or update an HPC cluster"""

    if request.method == 'GET':
        r = Response()
    pass

@app.route('/setup-run/begin-setup', methods=['GET'])
def setup_run():
    """Endpoint a user hits when they request to set up a model run.
    Lists available Workflows and returns these names to the user."""

    # verify the user's token
    claims = verify(request.headers.get('token'))
    if not claims:
        return Response(response='Invalid token', status=401) # Unauthorized code
    req = request
    # check what the user wants -- what process are they seeking to set up?
    if req.headers.get('begin-setup'):
        # list the available options
        # NOTE is this code safe here, or is this path condisidered relative?
        # TODO: list options in a prettier way
        opts = list(enumerate([f for f in os.listdir('cwl/templates/cwls')])) # if f.endswith('.cwl')]
        _opts = {str(i[0]): i[1] for i in opts}
        pload={'opts': _opts}
        r = Response(response=json.dumps(pload), status=200)
    return r

@app.route('/setup-run/workflow-selection', methods=['POST'])
def select_cwl():
    """Endpoint the user hits when they are POSTing their cwl selection.
    Only takes POST requests. Reads the user's selection, opens that .cwl
    Workflow and sends it back to the user to be prompted for input questions.
    """

    req = request
    claims = verify(req.headers.get('token'))
    if not claims:
        return Response(response='Invalid token', status=401)
    # these are requests where the user is giving information to the API
    conv = Converter()
    cwlfp = req.form.get('cwl')
    job_title = req.form.get('job_title')
    if not job_title: # default timestamp: year, month, day, hr, min, sec
        t = datetime.now().strftime('%Y%m%dT%H:%M:%S')
        job_title = 'job_{}'.format(t)
    fp = 'cwl/templates/cwls/{}'.format(cwlfp)
    # create an input template
    tpl = CWLHandler.gen_template(fp) # returns a str
    req, opt = CWLHandler.ro_inputs(tpl) # get required, optional inputs
    # send back the required and optional types along with workflow
    with open(fp.format(cwlfp)) as _wkflow:
        wkflow = _wkflow.read() # read string
        # send back a response that triggers questions for job inputs
        # add the cwlfp to the global storage dict, under the job title
        if (claims['email'] in gstor.keys()) and \
            ('jobs' in gstor[claims['email']].keys()): # don't overwrite existing
            gstor[claims['email']]['jobs'].update(
                {
                    job_title: {'requested_workflow': cwlfp, 'job': tpl}
                }
           )
        else: # create new
            gstor[claims['email']] = {
                'jobs': {job_title: {'requested_workflow': cwlfp, 'job': tpl}}
            }
        # create payload and dump as JSON
        payload = {'workflow': wkflow, 'required': req, 'optional': opt} 
        return Response(response=json.dumps(payload), status=200)

@app.route('/setup-run/load-job-input', methods=['POST'])
def load_user_inputs():
    """Take the user inputs and write them into the corresponding YAML job
    file. After writing, validates the job against each .cwl file the questions
    were generated from."""

    # use the passed filenames to load the files from templates; all
    # CWL and job files have the same name, just different extensions
    # TODO get cwlfp from global dict
    
    req = request
    # validate token 
    claims = verify(req.headers.get('token'))
    if not claims:
        return Response(response='Invalid token', status=401)
    email = claims['email'] # for easier access
    cwlfp = req.form.get('cwl')
    job_title = req.form.get('job_title') # title given by user
    errors = {}
    with open('cwl/templates/cwls/{}'.format(cwlfp)) as _cwl:
        conv = Converter()
        handler = CWLHandler() # instantiate handler
        job_inputs = req.form.get('job_inputs') # use in validation and YAML
        tpl = gstor.get(email).get('jobs').get(job_title).get('job')
        if not tpl: 
            return Response(response='No jobs created', status=404) # not found
        filled_tpl = handler.job_from_json(job_inputs, tpl) # create filled YAML template
        job_dict = safe_load(filled_tpl) # dict from YAML
        cwl_ = safe_load(_cwl)
        cwl_schema = conv.convert_workflow(cwl_) # valid JSONSchema Workflow
        valid, errs = handler.validate(job_dict, cwl_schema)
        if valid: # add to gstor
            gstor[email]['jobs'][job_title]['job_str'] = filled_tpl
    pld = {'errors': errors}
    r = Response(response=json.dumps(pld), status=200)
    return r


@app.route('/execute/begin', methods=['GET'])
def execute_begin():
    """List the executable workflow options."""

    req = request
    # validate token 
    claims = verify(req.headers.get('token'))
    if not claims:
        return Response(response='Invalid token', status=401)
    email = claims.get('email')
    # TODO implement check for permissions (JWTs)
    # send back the executable job options
    _opts = [k for k in gstor.get(email).get('jobs').keys()]
    if not _opts: # if no options avaialable, prompt user to setup
        pld = {'no_executables': 'No executables are avaiable.'+\
               ' Please run `setup` to set up your workflow run.'}
    else:
        pld = {'executable_options': _opts}
    return Response(response=json.dumps(pld), status=200)


@app.route('/execute/workflow', methods=['POST'])
def execute():
    """Execute a job with the `cwlrunner`. A POST request is expected to be
    passed with the corresponding .cwl and job files as JSON strings"""

    req = request
    # validate token 
    claims = verify(req.headers.get('token'))
    if not claims:
        return Response(response='Invalid token', status=401)
    email = claims.get('email')
    # TODO implement check for permissions (JWTs)
    job_title = req.form.get('job_title')
    if (gstor.get(email) is None): 
        pld = {'no_executables': 'please run setup-run'}
        return Response(response=json.dumps(pld), status=200)
    if (job_title not in gstor[email]['jobs'].keys()):
        # load job .yml files from storage
        _opts = [k for k in gstor.get(email).get('jobs').keys()]
        pld = {'executable_options': _opts}
        return Response(response=json.dumps(pld), status=200) # should this be 200?
    # get workflow, job_str by using job_title
    wkflow = gstor[email]['jobs'][job_title].get('requested_workflow')
    jobstr = gstor[email]['jobs'][job_title].get('job_str')
    if not jobstr: # send resp prompting user to finish setup
        return Response(status=406)
    # open tempfile in the same dir that the actual scripts are called from
    with NamedTemporaryFile(mode='a', dir='scripts') as _job:
        jobdict = safe_load(jobstr) # loads to dict
        _job.write(dump(jobdict, default_flow_style=False)) # write the YAML
        _job.seek(0)
        # use subprocess to launch the cwlrunner
        msg = ' ---------- Now executing {} ----------'.format(job_title)
        r = Response(response=json.dumps(msg), status=200)
        dir_ = os.path.abspath(os.curdir)
        subprocess.run([
                        'cwltool', 
                        '--debug', # cwl and job will be uploaded to wherever this is running
                        os.path.join(dir_, 'cwl', 'templates', 'cwls', wkflow),  
                        os.path.abspath(_job.name) # read the temporary file
                       ])
        return r


@app.route('/login', methods=['POST'])
def login():
    """Log into your FLEET account. Once a user POSTs the username and password
    information, this method uses boto3 and AWS Cognito to generate a Cognito 
    JWT, which will be passed back to the user in the response headers."""

    req = request
    username = req.form.get('username', None)
    password = req.form.get('password', None) 
    # NOTE here's an interesting question... secure HTTP in Flask?
    if (not username) or (not password):
        r = Response(status=406) # not acceptable
        return r
    # make the JWT
    try:
        jwt = generate_token(username, password)
        # verify the token     
        claims = verify(jwt)
        exp = claims['exp'] # expiration in seconds since 1970
        hdrs = {'token': jwt, 'exp': exp}
        r = Response(headers=hdrs, status=200)
    except Exception as e: # TODO need more specific exceptions
        hdrs = {'error': e}
        r = Response(headers=hdrs, status=401) # return bad login
    return r

def generate_token(username, password):
    """Generate a Cognito token

    :param str username: username
    :param str password: password
    """

    # Amazon Cognito User Pool - authenticate
    client = boto3.client('cognito-idp', region_name=conf['region'])
    # TODO region could change with user?
    aws = AWSSRP( # AWSSRP -> AWS Secure Remote Password protocol
        username = username,
        password = password,
        pool_id = conf['pool_id'],
        client_id = conf['client_id'],
        client = client
    )
    # get tokens
    tokens = aws.authenticate_user()
    id_token = tokens['AuthenticationResult']['IdToken'] 
    return id_token


# ===========
# run the app
# ===========

def main():
    """
    Launches the application.
    """

    return app.run(
                   host=conf['HOST'],
                   port=conf['PORT'],
                   debug=conf['DEBUG']
                   )
if __name__ == '__main__':
	main()
