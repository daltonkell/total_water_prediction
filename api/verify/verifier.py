import boto3
import getpass
import json
import requests
import time
from jose import jwk, jwt
from jose.utils import base64url_decode

class Verify(object):
    """Tool to verify a FLEET user"""

    def __init__(self):
        pass

    @staticmethod
    def match_key(key_id, json):
        """Search a JSON dict and return the key with the matching keyID along
        with the algorithm to use with it.

        :param str key_id: key ID
        :param dict json: json dict
        :returns tuple str, str
        """

        for _kdict in json['keys']: # json expected to have this field
            if _kdict['kid'] == key_id:
                return _kdict

    def verify_token(self, token, keys_url, client_id, keys=None):
        """
        Verify a user's token hasn't been tampered with. Returns claims after 
        verification.

        :param dict token: JWT to verify
        :param str keys_url: URL to get public keys
        :param str client_id: client ID to match to aud in token
        :param dict keys: dictionary of JWKs; default None
        """

        # get the JSON dict of the public keys
        keys = keys if keys else requests.get(keys_url).json()
        # get unverified header to get the key
        header = jwt.get_unverified_header(token)
        # get matching key, construct key JWK object for verification
        _kid = header['kid']
        key = jwk.construct(self.match_key(_kid, keys))
        # split apart the encoded token to the parts we need
        msg, encoded_sig = str(token).rsplit('.', 1) # max split 1
        # decode the signature
        decoded_sig = base64url_decode(encoded_sig.encode('utf-8'))
        # verify
        if not key.verify(msg.encode('utf-8'), decoded_sig):
            print('WHOA! NOT VERIFIED!')
            return False
        # check token expiration using unverified claims
        uvclaims = jwt.get_unverified_claims(token)
        if time.time() > uvclaims['exp']:
            print('Token is expired')
            return False
        # check the audience matches our client id
        if uvclaims['aud'] != client_id:
            print('Wrong audience')
            return False
        print('\nCLAIMS\n{:*^120}\n{}\n{:*^120}\n'.format('', uvclaims, ''))
        return uvclaims

# IDEA Let's make a decorator here which we can wrap the routes with. This
# decorator will check (local?) (global?) variables for a set of claims and
# confirm whether the token has expired or not, or has the correct permissions
# for the particular service that route will link to
class Gatekeeper(object):
    """Decorator. Check to see if a token is expired, and has the allowed
    permissions to use a particular service."""

    def __init__(self, func, claims):
        pass
