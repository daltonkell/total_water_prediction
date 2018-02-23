#!/usr/bin/env python
# -*- coding: utf-8 -*-

import boto3
import configparser
import getpass
import os
from warrant.aws_srp import AWSSRP
from warrant.exceptions import ForceChangePasswordException

def login(args):
    if not args.username:
        username = input('Enter username:')
    password = getpass.getpass()
    print('Printing password for testing purposes: "{}"'.format(password))
    # Parse configuration
    config = configparser.ConfigParser()
    config.read(['fleet.cfg', os.path.expanduser('~/.fleet.cfg')])
    cognito = config['cognito']

    # Amazon Cognito User Pool - authenticate
    client = boto3.client('cognito-idp')
    aws = AWSSRP(
        username = username,
        password = password,
        pool_id = cognito['pool_id'],
        client_id = cognito['client_id'],
        client = client
    )
    try:
        tokens = aws.authenticate_user()
    except ForceChangePasswordException:
        ntries = 3
        while ntries > 0:
            try:
                ntries -= 1
                new_password = getpass.getpass('Enter new password: ')
                tokens = aws.set_new_password_challenge(new_password)
                break
            except Exception as e:
                errormessage = e.response['ResponseMetadata']['HTTPHeaders']['x-amzn-errormessage']
                print('\tERROR: {}'.format(errormessage))
        if ntries == 0:
            print('ERROR: Too many attempts to set password')
            return {}
    # TODO: implement PasswordResetRequiredException

    # Amazon Cognito Federated Identities - get credentials
    cognito_id = boto3.client('cognito-identity')
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

    return response
