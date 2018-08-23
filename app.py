from flask import Flask, request, jsonify, Response
import os
import sys

# instantiate the application
app = Flask(__name__)

# configuration--load up the config file
app.config.from_json('config.json')

# define routes--where requests will be handled
@app.route('/')
def index():
    """Simple Index route"""
    return jsonify(status='hello')

@app.route('/login', methods=['GET', 'POST']) # expects only GET, POST
def fleet_welcome(): # can't put parameters into this
    """Returns a mock response to a GET request to login"""

    if request.method == 'GET':
        r = Response(response='You are now ready to log in', status=200)
    elif request.method == 'POST':
        user = request.headers['username']
        # within here there will be some sort of authentication
        welcome = '\n{:*^80}\n'.format('  Welcome to FLEET, {}  '.format(user))
        r = Response(response=welcome, status=200)
    else:
        r = Response(response='Only GET and POST allowed in login', status=400)
    return r

@app.route('/list', methods=['GET'])
def list_clusters():
    """List all clusters. If the passed request headers contain the stack name,
    list the stacks with the specified name"""

    if not request.method == 'GET':
        return Response(response='Please provide a GET request', status=400)
    if request.headers.get('stack_name'):
        sn = request.headers.get('stack_name')
        resp = {'stack1{}'.format(sn): 'clusterXYZ'}
    else:
        resp = ['cluster1, cluster2, cluster3']
    return jsonify(status=resp)

@app.route('/create-and-update', methods=['GET', 'POST'])
def create_update():
    """Create or update an HPC cluster"""

    if request.method == 'GET':
        r = Response()
    pass

# run the app
def main():
    """
    Launches the application.
    """

    return app.run(
                   host=app.config['HOST'],
                   port=app.config['PORT'],
                   debug=app.config['DEBUG']
                   )
if __name__ == '__main__':
	main()
