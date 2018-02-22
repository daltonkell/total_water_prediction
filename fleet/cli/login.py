#!/usr/bin/env python
# -*- coding: utf-8 -*-

import boto3
import configparser
import os
from warrant.aws_srp import AWSSRP

def login(username, password):

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
    tokens = aws.authenticate_user()

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
