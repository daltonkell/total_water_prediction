import argparse
import configparser # built in config file parser
import getpass
import logging
import os
import requests
import sys
import tempfile
from fleet.cli.login import login
from cwl import CWLHandler

# Parse configuration
config = configparser.ConfigParser()
config.read(['.fleet.cfg', os.path.expanduser('../../.fleet.cfg')])

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


def test_cwl(args, config): # NOTE config doesn't do anything for development, this ish is hardcoded
    """Test the basic functionality of a CWL workflow"""
    
    cwl = CWLHandler()
    # test the CWL writer
    cwl.invoke_cwl() # pass the filepath so cwl-runner can handle this


# logging configuration

# -----------
# CLI OPTIONS # NOTE these may be moved out like `login()` to preserve readability
# -----------

def main():
    # call logger
    # parent parser contains common options
    parser = argparse.ArgumentParser(description='fleet is a tool that can be used by IOOS modelers for HPC tasks')
    # common arguments
    parser.add_argument('-c', '--config', type=str,
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


    # DEVELOPMENT ===
    _test_cwl = subparsers.add_parser('test_cwl', help='test CWL')
    _test_cwl.set_defaults(func=test_cwl)

    # parse 'em
    args = parser.parse_args()
    # logger.debug(args)
    args.func(args, config) # trigger the functions which were specified by the args
