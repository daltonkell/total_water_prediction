import boto3
import cryptography # need whole lib?
import getpass
import json
import requests
from warrant.aws_srp import AWSSRP # warrant for AWS Cognito authentication
from warrant.exceptions import ForceChangePasswordException

class Verify(object):
    """Tool to verify a FLEET user"""

    def __init__(self):
        pass

    @staticmethod
    def datetime_handler(x):
        """Return a datetime in isoformat if instance of datetime
        :param datetime.datetime instance x
        """

        if isinstance(x, datetime.datetime):
            return x.isoformat()
        raise TypeError("Unknown type")

    @staticmethod
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

    def verify_token(self, token):
        """
        Verify a user's token hasn't been tampered with.

        :param dict token: JWT to verify
        """

        # get unverified header to get the key to get the verified header
        # get the JSON dict of the public keys
        keys_json = requests.get(cognito['keys_url']).json()

        # TODO use cryptography to decode

        header = jwt.decode(id_token).header
        _key = header['kid']
        # get matching key, use key to verify
        key, alg = self.match_key(_key, keys_json)
        decoded = jwt.decode(id_token, key, algorithms=alg)

        print('\n{:*^120}\n{}\n{:*^120}\n'.format('', decoded, ''))
