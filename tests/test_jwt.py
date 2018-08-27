# import configparser # built in config file parser
import getpass
import os
import json
import verify
import unittest
from jose import jwk, jwt
from jose.utils import base64url_decode

class JWTTest(unittest.TestCase):
    """Simple class to test if the JWT verification works as planned"""


    def test_jwt_verification(self):
        """Test the JWT verification."""
        pass


if __name__ == '__main__':
    unittest.main()
