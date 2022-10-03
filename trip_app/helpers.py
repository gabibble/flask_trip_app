from functools import wraps

import secrets

from flask import request, jsonify, json


import decimal

def token_required(our_flask_function):
    @wraps(our_flask_function)
    def decorated(*args, **kwargs):
        token = None

        if 'x-access-token' in request.headers:
            token = request.headers['x-access-token'].split(' ')[1]
            print(token)
        if not token:
            return jsonify({'message': 'Token is Missing! Yikes!'}), 401
        return our_flask_function(token, *args, **kwargs)
    return decorated 

class JSONEncoder(json.JSONEncoder):
    def default (self, obj):
        if isinstance(obj, decimal.Decimal):
            #conv decimals into strings
            return str(obj)
        return super (JSONEncoder, self).default(obj)