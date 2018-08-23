#!/usr/bin/env python
# -*- coding: utf-8 -*-

import boto3
import configparser # built in config file parser
import getpass
import json
import os
import requests
from warrant.aws_srp import AWSSRP # warrant for AWS Cognito authentication
from warrant.exceptions import ForceChangePasswordException

def datetime_handler(x):
     if isinstance(x, datetime.datetime):
         return x.isoformat()
     raise TypeError("Unknown type")


def login(args, config):
    """Log into your FLEET account

    Parameters
    ----------
    args : argparse.ArgumentParser parser
           Contains the optional aguments passed in via the CLI
    config : configparser object
           contains configuration information in key-value pairs"""

    cognito = config['cognito']
    api = config['API']

    # send a GET request to API
    r = requests.get(api['login']) # sends a get request to a defined route
    if r.status_code == 200:
        # get username and password
        if not args.user:
            username = input('Enter username: ')
        else:
            username = args.user

        # API will be expecting a POST request (most likely)
        cred_post = requests.post(
            api['login'],
            headers={
                'username': username,
                # this will probably contain the password as well,
                # possibly the below tokens
                }
            )
        if cred_post.status_code == 200:
            print(cred_post.text)
        return # for now -- state of development

        # ----------------------------------------------------------------------

        password = getpass.getpass('Enter password:')
        print('Printing password for testing purposes: \n\t"{}"'.format(password))

        # Amazon Cognito User Pool - authenticate
        client = boto3.client('cognito-idp', region_name=cognito['region'])  # TODO region could change with user
        aws = AWSSRP(                # AWSSRP -> AWS Secure Remote Password protocol
            username = username,
            password = password,
            pool_id = cognito['pool_id'],
            client_id = cognito['client_id'],
            client = client
        )
        try:
            # get tokens
            tokens = aws.authenticate_user()
            # debug by printing JSON
            print(json.dumps(tokens, default=datetime_handler, indent=4, sort_keys=True))
            print('\n{:*^120}\n'.format(''))
            print([(k, v) for k, v in cognito.items()])
            print('\n{:*^120}\n'.format(''))

        except ForceChangePasswordException:
            ntries = 3 # give users 3 tries to set a new password
            while ntries > 0:
                try:
                    ntries -= 1
                    new_password = getpass.getpass('Enter new password: ')
                    # TODO make a password strength validator? Requirements?
                    tokens = aws.set_new_password_challenge(new_password)
                    break
                except Exception as e:
                    errormessage = e.response['ResponseMetadata']['HTTPHeaders']['x-amzn-errormessage']
                    print('\tERROR: {}'.format(errormessage))
            if ntries == 0:
                print('ERROR: Too many attempts to set password')
                return {}
        # TODO: implement PasswordResetRequiredException

        # ----------------------
        # "ADVANCED" CREDENTIALS
        # ----------------------

        # Amazon Cognito Federated Identities - get credentials
        cognito_id = boto3.client('cognito-identity', region_name=cognito['region'])
        id_token = tokens['AuthenticationResult']['IdToken']
        response = cognito_id.get_id(
            IdentityPoolId = cognito['identity_pool_id'],
            Logins = {
                cognito['login']: id_token
            }
        )
        identity_id = response['IdentityId']

        # Amazon Cognito Federated Identities - get credentials
        response = cognito_id.get_credentials_for_identity(
            IdentityId = identity_id,
            Logins = {
                cognito['login']: id_token
            }
        )
        # where is this response going?
        return response
