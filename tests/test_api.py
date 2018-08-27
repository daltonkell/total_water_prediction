import os
import app
import requests
import unittest

from flask import Flask, request, jsonify, Response

class APIUnittest(unittest.TestCase):
    """Mock API unit tests. These unit tests do not test the functionality of
    the command-line-interface, but rather only the functionality of the Flask
    application itself. See the CLIUnittest class for command line tests."""

    def setUp(self):
        """Sets up objects before every test. Using the Flask.test_client()
        allows us to send requests to the app without running it on a host or
        port directly."""

        self.app = app.app.test_client()
        self.app.testing = True # exceptions will propogate to test client

    def test_login(self):
        """Send a GET and POST request to the login endpoint of `fleet`."""

        r = self.app.get('/login')
        assert 'You are now ready to log in'.encode() in r.data # encode str to bytes
        r = self.app.post('/login', headers={'username': 'TESTUSER'})
        expected = '\n*************************  Welcome to FLEET, TESTUSER  *************************\n'.encode()
        assert expected in r.data
        # test only GET and POST accepted
        r = self.app.put('/login')
        assert 'Method Not Allowed'.encode() in r.data

if __name__ == '__main__':
    unittest.main()
