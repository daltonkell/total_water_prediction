import argparse
import configparser # built in config file parser
import getpass
import json
import logging
import os
from datetime import datetime
from fleet.cli.ask_job import ask, ask_wkflow
from urllib.error import HTTPError
from urllib.parse import urlencode
from urllib.request import Request, urlopen
import pdb

# Get root of project and parse configuration file(s)
config = configparser.ConfigParser()
config.read([os.path.join(os.path.abspath(os.curdir), '.fleet.cfg')])
if not os.path.exists(os.path.join(os.getcwd(), 'jwt.tmp')):
    # make jwtfile
    f = open(os.path.join(os.getcwd(), 'jwt.tmp'), 'w')
    f.close() # close the file
jwtfile = open(os.path.join(os.getcwd(), 'jwt.tmp'), 'r') # opens JWT temp file

def create(args):
    """
    Creates an HPC fleet using the passed arguments.

    Parameters
    ----------
    args :
    """
    print('Creates an HPC fleet with given name "{}"'.format(args.fleet_name))


def configure(args):
    """
    Configures an HPC fleet using the passed arguments.

    Parameters
    ----------
    args :
    """
    print('Configures HPC fleet with given name "{}"'.format(args))


def status(args):
    """
    Yields the status of an HPC fleet.

    Parameters
    ----------
    args :
    """
    print('Yields HPC fleet "{}" status'.format(args))


def list(args, config):
    """
    Lists all the started and stopped HPC fleets.

    Parameters
    ----------
    args : argparse.ArgumentParser parser
           Contains the optional aguments passed in via the CLI"""

    api = config['API']
    headers = {}
    if args.stack_name:
        headers = {'stack-name': args.stack_name} # put stack name in headers
    r = requests.get(api['list'], headers=headers) # send the GET request
    print('\nThe following clusters exist:\n{}\n'.format(r.json()))
    return


def delete(args, config):
    """
    Deletes an HPC fleet

    Parameters
    ----------
    args :
    """
    print('Deletes a selected HPC fleet with name "{}"'.format(args.fleet_name))


def instances(args, config):
    """
    This definitely does something.
    """
    print('Does something? More to come.')


def update(args, config):
    """
    Updates an HPC fleet

    Parameters
    ----------
    args :
    """
    print('Updates an HPC fleet with name "{}"'.format(args.fleet_name))


def version(args, config):
    """
    Lists the version of the HPC fleet

    Parameters
    ----------
    args :
    """
    print('HPC fleet "{}"; version: '.format(args.fleet_name))


def start(args, config):
    """
    Starts up an HPC fleet

    Parameters
    ----------
    args :
    """
    print('Starts an HPC fleet: "{}"'.format(args))


def ssh(args, config):
    """
    Run an ssh to the master node... or something...

    Parameters
    ----------
    args :
    """
    print('{}'.format(ssh.__doc__))


def stop(args, config):
    """
    Stops an HPC fleet

    Parameters
    ----------
    args :
    """
    print('Stops an HPC fleet "{}"'.format(args))


def execute(args, config):
    """
    Execute a CWL Workflow remotely. Only Workflows where job files have been
    properly set up and validated will run. In the case a user selects a Work-
    flow which has not been completely set up, they will be prompted to comple-
    te the setup.
    
    :param argparse.ArgumentParser.arguments args: args from cmd line
    :param configparser.ConfigParser config: parser loaded with config file"""

    token = jwtfile.read()
    api = config['API']
    if not args.job: # users would supply name of workflow to execute
        hdrs = {'token': token}
        r = Request(api['execute-begin'], headers=hdrs)
        # if marked as unverified, we must login first to get a new token
        try:
            resp = urlopen(r)
        except HTTPError as e:
            # TODO deal with plain 400
            if resp.getcode() in [401, 406]:
                print('Your token is unverified. Please log in for another token.')
                login(args, config) # trigger login method
            else:
                print('Expected a 401 or 406, got a {}'.format(e.getcode()))
            return
        # print out options to command line
        jsn = json.loads(resp.read().decode())
        execs = jsn.get('executable_options')
        print('\nPlease select a job and re-run this command'\
              ' with the `--job <job_title>` option to execute.\n')
        print('Executable Jobs\n---------------')
        for _e in execs:
            print(_e)
        return
    elif args.job:
        job_title = args.job
        hdrs = {'token': token}
        pld = {'job_title': job_title}
        r = Request(api['execute-workflow'], data=urlencode(pld).encode(), headers=hdrs)
        #r = requests.post(api['execute-workflow'], data=pld, headers=hdrs)
        # we expect a response to ask us questions
        try:
            resp = urlopen(r)
        except HTTPError as e:
            if e.getcode() == 401:
                print('Uh oh, looks like your token has expired. Please re-login.')
                return
            elif e.getcode() == 406:
                m = 'You need to finish setting up the run before proceeding.'+\
                    '  Re-run the `setup-run` command with your CWL selection.'
                print(m)
            else:
                print('Expected 401, 406, got {}'.format(e.getcode()))
            return
        # print out the output from the execution
        jsn = json.loads(resp.read().decode())
        print(jsn)
        return

def login(args, config):
    """Makes a POST request to the API with a username and password and in turn
    receives a JWT. Writes the JWT to a local file, which will be passed inside
    the headers of every other request.

    :param argparse.ArgumentParser.arguments args: args from cmd line
    :param configparser.ConfigParser config: parser loaded with config file"""
 
    api = config['API']
    username = args.__dict__.get('user')
    if not username:
        username = input('Enter username: ')
    password = getpass.getpass('Enter password: ')
    # send POST request to login with username and password
    pld = {'username': username, 'password': password}
    h = {'blank': 'header'}
    r = Request(api['login'], data=urlencode(pld).encode(), headers=h, method='POST')
    try:
        resp = urlopen(r)
    except HTTPError as e:
        if e.getcode() == 401:
            print('Your account is not authorized for this action')
        if e.getcode() == 406: # unacceptable
            print('406 mate, you sent something bad')
        print('Bad login detected. Please check your username/password.')
        return
    hdr_in = {}
    for i in resp.getheaders():
        hdr_in[i[0]] = i[1] # create dict from list of tuples 
    token = hdr_in.get('token')
    exp = hdr_in.get('exp') # expiration
    _ex = datetime.fromtimestamp(int(exp))
    ex = _ex.strftime('%Y-%m-%dT%H:%M:%S')
    # write JWT to local tempfile--can be overwritten with new JWTs
    # TODO make tempfile ~/.jwt or something
    tmp = 'jwt.tmp'
    pth = os.getcwd()
    with open(os.path.join(pth, tmp), 'w+') as _jwt:
        _jwt.write(token) # write token to file
    expr = ' Your session will expire at {} '.format(ex)
    m = '\n{:*^80}\n{:*^80}\n'.format('  Welcome to FLEET, {}  '.format(username), expr)
    print(m)


def setup_run(args, config):
    """Allow a user to set up a model run from the ground up. Sends a GET
    request to /setup-run and receives a list of available .cwl and job .yml
    files to run. The user is then prompted to re-run this command with the 
    `--cwl <cwl file>` and `--job <job file>` options, which sends a POST 
    request back to the API with the filenames in the header. The API then 
    takes care of cwl-to-json conversion and validation.

    :param argparse.ArgumentParser.arguments args: args from cmd line
    :param configparser.ConfigParser config: parser loaded with config file""" 

    token = jwtfile.read() # read the JWT so we can send it in the header
    api = config['API']
    if not args.cwl: # beginning of process
        # request to get available options
        hdrs = {'begin-setup': 'True', 'token': token}
        r = Request(api['setup-run-start'], headers=hdrs)
        try:
            resp = urlopen(r)
            # if marked as unverified, we must login first to get a new token
        except HTTPError as e:
            # TODO deal with plain 400
            if e.code in [401, 406]:
                print('Your token is unverified. Please log in for another token.')
                login(args, config) # trigger login method
                return
            else:
                print('Was expecting a 401 or 406, got a {}'.format(e.code))
                return
        # print out options to command line
        jsn = json.loads(resp.read().decode()).get('opts', None)
        print('\nPlease select a CWL and job (.yml) file and re-run this command'\
              ' with the `--cwl <cwl>` option:\n')
        print('Available Options\n----------------')
        for k, v in jsn.items():
            print('{}: {}'.format(k, v))
        return
    cwl_file = args.cwl # get the .cwl
    # ask for a job title so the sevrer can store this
    title = input('Please enter a title for the job you are creating: ')
    hdrs = {'cwl-input': 'True', 'cwl': cwl_file, 'token': token}
    pld = {'cwl': cwl_file, 'job_title': title}
    r = Request(api['setup-run-select-wkflow'], data=urlencode(pld).encode(), headers=hdrs, method='POST')
    try:
        resp = urlopen(r)
        # we expect a response to ask us questions
    except HTTPError as e:
        if e.getcode() in [401, 406]:
            print('Uh oh, looks like your token has expired. Please re-login.')
        elif e.getcode() == 404: # notfound
            print('A template couldn\'t be properly generated for that Workflow.')
        else:
            print('Expected 401, 404, 406, got {}'.format(e.getcode()))
        return
    # invoke the questions prompt; iterate through each CWL key
    job_input_dict = {} # initialize empty dict to be updated
    # send the inputs back as JSON
    print('You requested the following Workflow: \n')
    jsn = json.loads(resp.read().decode()) # bytes to str to dict
    wkflow = jsn.get('workflow', None)
    print(wkflow)
    print('\n')
    _req = jsn.get('required') # dict, but only because we're using requests lib...
    _opt = jsn.get('optional')
    job_input_dict.update(ask_wkflow(_req, _opt))
    job_inputs = json.dumps(job_input_dict)
    d = {
            'cwl': cwl_file, 
            'job_inputs': job_inputs,
            'job_title': title, 
        }
    h = {'token': token}
    r = Request(api['setup-run-job-input'], data=urlencode(d).encode(), headers=h, method='POST')
    try:
        resp = urlopen(r)
    except HTTPError as e:
        if e.getcode() in [401, 406]:
            print('Token expired; please re-login')
        else:
            print('Huh?')
        return
    jsn = json.loads(resp.read().decode())
    if jsn.get('errors', {}) == {}: # empty dict means no errors!
        print('Your JOB sucessfully validated.')
    else: # print all errors and ask person to do it again
        #print(r.json.get('errors'))
        print(jsn.get('errors'))
    return


# logging configuration?

# -----------
# CLI OPTIONS # NOTE these may be moved out like `login()` to preserve readability
# -----------

def main():
    # call logger
    # parent parser contains common options
    parser = argparse.ArgumentParser(description='fleet is a tool that can be used by IOOS modelers for HPC tasks')
    # common arguments
    parser.add_argument('-cfg', '--config', type=str,
                         help='specify an alternative configuration file')
    parser.add_argument('-nw', '--nowait', type=str,
                          help='Do not wait for stack events')
    parser.add_argument('-nr', '--norollback', type=str,
                        help='Disable stack rollback on an error')
    parser.add_argument('-u', '--template-url',
                        type=str, help='Supply a URL for custom template')
    parser.add_argument('-t', '--cluster-template',
                        type=str, help='Supply the filepath to a template')
    parser.add_argument('-p', '--extra-parameters',
                        type=str, help='Supply extra parameters')
    parser.add_argument('-r', '--region', dest='region',
                        help='specify a specific region to connect to',
                        default=None)

    # waiting argument?

    subparsers = parser.add_subparsers()
    subparsers.required = True
    # subparser destination

    # NOTE subparser objects cannot be named the same as their functions, or
    # argparse will attempt to call the object as a method and break

    # user login
    _login = subparsers.add_parser('login', help='Login with user credentials')
    _login.add_argument('-u', '--user', type=str, default=None,
                       help='enter username')
    _login.set_defaults(func=login)

    # create clusters
    _create = subparsers.add_parser('create', help='Creates an HPC fleet')
    _create.add_argument('--fleet_name', type=str, default=None,
                        help='create an HPC fleet with provided name')
    _create.add_argument('-g TAGS', '--tags TAGS', type=str,
                        help='Tags to be added to stack. JSON formatted\n'+\
                        'string encapsulated by single quotes')
    _create.set_defaults(func=create)

    # update clusters
    _update = subparsers.add_parser('update', help='Updates an HPC fleet')
    _update.add_argument('--fleet_name', type=str, default=False,
                    help='update an HPC fleet with the provided name')
    _update.set_defaults(func=update)

    # delete clusters
    _delete = subparsers.add_parser('delete', help='Deletes an HPC fleet')
    _delete.add_argument('--fleet_name', type=str, default=None,
                        help='delete an HPC fleet with the provided name')
    _delete.set_defaults(func=delete)

    # start up clusters
    _start = subparsers.add_parser('start', help='starts up an HPC fleet')
    _start.add_argument('--fleet_name', type=str, default=None,
                       help='Fires up an HPC fleet with the provided name')
    _start.set_defaults(func=start)

    # stop running clusters
    _stop = subparsers.add_parser('stop', help='stops an HPC fleet')
    _stop.add_argument('--fleet_name', type=str, default=None,
                       help='Shuts down an HPC fleet with the provided name')
    _stop.set_defaults(func=stop)

    # get the status of clusters
    _status = subparsers.add_parser('status',
                                    help='pull current status of the fleet')
    _status.add_argument('--fleet_name', type=str, default=None,
                   help='show the status of cfncluster with the provided name.')
    _status.set_defaults(func=status)

    # list stacks -- P.S. what are stacks?
    _list = subparsers.add_parser('list',
                          help='display a list of stacks associated with fleet')
    _list.add_argument('--stack-name', type=str, default=None,
                       help='Name of the stack name you wish to list')
    _list.set_defaults(func=list)

    # list all the instances in a fleet
    _instances = subparsers.add_parser('instances',
                              help='display a list of all instances in a fleet')
    _instances.add_argument("fleet_name", type=str, default=None,
                        help='show the status of fleet with the provided name.')
    _instances.set_defaults(func=instances)

    # create fleet config
    _configure = subparsers.add_parser('configure',
                                    help='creating initial fleet configuration')
    _configure.set_defaults(func=configure)

    # ssh
    _ssh= subparsers.add_parser('ssh',
                    help='Runs ssh to the master node, with username and ip\n'+\
                                      'filled in based on the provided cluster')
    _ssh.set_defaults(func=ssh)

    # get version
    _version = subparsers.add_parser('version',
                                    help='display version of fleet')
    _version.set_defaults(func=version)

    # set up a model run
    _setup_run = subparsers.add_parser('setup-run',
                                      help='Set up a model run')
    _setup_run.set_defaults(func=setup_run)
    # ability to pass in .cwl and .yml job files
    _setup_run.add_argument('--cwl', type=str, help='specify a CWL .cwl file')
    _setup_run.add_argument('--job', type=str, help='specify a CWL job file (.yml)')

    # execute a workflow
    _execute = subparsers.add_parser('execute', help='Execute a created job')
    _execute.set_defaults(func=execute)
    _execute.add_argument('--job', type=str, help='Specify the job\
                           file')

    # parse 'em
    args = parser.parse_args()
    # logger.debug(args)
    args.func(args, config) # trigger the functions which were specified by the args
