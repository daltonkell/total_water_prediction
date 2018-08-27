#!/usr/bin/env python
# -*- coding: utf-8 -*-

import boto3
import getpass
import json
import os
import requests
from warrant.aws_srp import AWSSRP # warrant for AWS Cognito authentication
from warrant.exceptions import ForceChangePasswordException

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


        if cognito.get('password', None): # use password in config if it exists
            password = cognito['password']
        else:
            password = getpass.getpass('Enter password:')
        print('Printing password for testing purposes: \n\t"{}"'.format(password))


        token = generate_token(username, password, cognito)

        # send a POST request with the token in the header
        cred_post = requests.post(
            api['login'],
            headers={
                'username': username,
                'cognitoToken': token,
                'keys_url': cognito['keys_url'],
                'client_id': cognito['client_id']
                }
            )

        print(cred_post.text)

def generate_token(username, password, cognito):
    """Generate a Cognito token

    :param str username: username
    :param str password: password
    :param dict cognito: AWS Cognito configuration settings
    """

    # Amazon Cognito User Pool - authenticate
    client = boto3.client('cognito-idp', region_name=cognito['region'])
    # TODO region could change with user
    aws = AWSSRP( # AWSSRP -> AWS Secure Remote Password protocol
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
        # print(json.dumps(tokens, default=self.datetime_handler, indent=4, sort_keys=True))
        # print('\n{:*^120}\n'.format(''))
        # print([(k, v) for k, v in cognito.items()])
        # print('\n{:*^120}\n'.format(''))

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

    # ======================================================================
    # response = cognito_id.get_id(
    #     IdentityPoolId = cognito['identity_pool_id'],
    #     Logins = {
    #         cognito['login']: id_token
    #     }
    # )
    # identity_id = response['IdentityId']
    #
    # # Amazon Cognito Federated Identities - get credentials
    # response = cognito_id.get_credentials_for_identity(
    #     IdentityId = identity_id,
    #     Logins = {
    #         cognito['login']: id_token
    #     }
    # )
    # # where is this response going?
    # print('\nRESPONSE\n{}'.format(response))

    return id_token

def datetime_handler(x):
    """Return a datetime in isoformat if instance of datetime
    :param datetime.datetime instance x
    """

    if isinstance(x, datetime.datetime):
        return x.isoformat()
    raise TypeError("Unknown type")

def match_key(keyID, json):
    """Search a JSON dict and return the key with the matching keyID along
    with the algorithm to use with it.

    :param str keyID: key ID
    :param dict json: json dict
    :returns tuple str, str
    """

    for _kdict in json['keys']:
        print(_kdict)
        if _kdict['kid'] == keyID:
            return _kdict['kid'], _kdict['alg']
