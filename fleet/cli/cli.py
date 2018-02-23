import argparse
import getpass
import logging
import os
import sys

from login import login


def create(args):
    """
    Creates an HPC fleet using the passed arguments.

    parameters
    ----------
    args :
    """
    print('Creates an HPC fleet with given name "{}"'.format(args.fleet_name))


def configure(args):
    """
    Configures an HPC fleet using the passed arguments.

    parameters
    ----------
    args :
    """
    print('Configures HPC fleet with given name "{}"'.format(args))


def status(args):
    """
    Yields the status of an HPC fleet.

    parameters
    ----------
    args :
    """
    print('Yields HPC fleet "{}" status'.format(args))


def list(args):
    """
    Lists all the started and stopped HPC fleets.

    parameters
    ----------
    asrgs :
    """
    print('Lists all HPC fleets.')


def delete(args):
    """
    Deletes an HPC fleet

    parameters
    ----------
    args :
    """
    print('Deletes a selected HPC fleet with name "{}"'.format(args.fleet_name))


def instances(args):
    """
    This definitely does something.
    """
    print('Does something? More to come.')


def update(args):
    """
    Updates an HPC fleet

    parameters
    ----------
    args :
    """
    print('Updates an HPC fleet with name "{}"'.format(args.fleet_name))


def version(args):
    """
    Lists the version of the HPC fleet

    parameters
    ----------
    args :
    """
    print('HPC fleet "{}"; version: '.format(args.fleet_name))


def start(args):
    """
    Starts up an HPC fleet

    parameters
    ----------
    args :
    """
    print('Starts an HPC fleet: "{}"'.format(args))


def stop(args):
    """
    Stops an HPC fleet

    parameters
    ----------
    args :
    """
    print('Stops an HPC fleet "{}"'.format(args))


# logging here?


def main():
    # call logger

    parser = argparse.ArgumentParser(description='fleet is a tool that can be used by IOOS modelers for HPC tasks')
    # specify config file?
    # specify connection region?
    # waiting argument?

    subparsers = parser.add_subparsers()
    subparsers.required = True
    # subparser destination


    plogin = subparsers.add_parser('login', help='Login with user credentials')
    plogin.add_argument('username', type=str, default=None,
                       help='enter username')
    plogin.set_defaults(func=login)

    pcreate = subparsers.add_parser('create', help='Creates an HPC fleet')
    pcreate.add_argument('fleet_name', type=str, default=None,
                        help='create an HPC fleet with provided name')
    pcreate.set_defaults(func=create)

    pupdate = subparsers.add_parser('update', help='Updates an HPC fleet')
    pupdate.add_argument('fleet_name', type=str, default=False,
                        help='update an HPC fleet with the provided name')
    pupdate.set_defaults(func=update)

    pdelete = subparsers.add_parser('delete', help='Deletes an HPC fleet')
    pdelete.add_argument('fleet_name', type=str, default=None,
                        help='delete an HPC fleet with the provided name')
    pdelete.set_defaults(func=delete)

    pstart = subparsers.add_parser('start', help='starts up an HPC fleet')
    pstart.add_argument('fleet_name', type=str, default=None,
                       help='Fires up an HPC fleet with the provided name')
    pstart.set_defaults(func=start)

    pstop = subparsers.add_parser('stop', help='stops an HPC fleet')
    pstop.add_argument('fleet_name', type=str, default=None,
                       help='Shuts down an HPC fleet with the provided name')
    pstop.set_defaults(func=stop)

    pstatus = subparsers.add_parser('status', help='pull current status of the fleet')
    pstatus.add_argument("fleet_name", type=str, default=None,
                        help='show the status of cfncluster with the provided name.')
    pstatus.set_defaults(func=status)

    plist = subparsers.add_parser('list', help='display a list of stacks associated with fleet')
    plist.set_defaults(func=list)

    pinstances = subparsers.add_parser('instances', help='display a list of all instances in a fleet')
    pinstances.add_argument("fleet_name", type=str, default=None,
                        help='show the status of fleet with the provided name.')
    pinstances.set_defaults(func=instances)

    pconfigure = subparsers.add_parser('configure', help='creating initial fleet configuration')
    pconfigure.set_defaults(func=configure)

    pversion = subparsers.add_parser('version', help='display version of fleet')
    pversion.set_defaults(func=version)

    args = parser.parse_args()
    # logger.debug(args)
    args.func(args)
