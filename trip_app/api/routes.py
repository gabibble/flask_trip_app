from flask import Blueprint, request, jsonify 
from trip_app.models import db, Trip, trip_schema, trips_schema
from trip_app.helpers import token_required

api = Blueprint('api', __name__, url_prefix = '/api')

@api.route('/getdata')
@token_required
def getdata(current_user_token):
    return{'token': current_user_token}


@api.route('/create_trip', methods = ['POST'])
# @token_required
def create_trip(current_user_token):
    name = request.json['name']
    descrip = request.json['descrip']
    origin = request.json['origin']
    dest = request.json['dest']
    guests = request.json['guests']
    nights = request.json['nights']
    accom = request.json['accom']
    month = request.json['month']
    mode = request.json['mode']
    user_token = request.json['user_token']
    
    print(current_user_token.token)

    trip = Trip(name, descrip, origin, dest, guests, nights, accom, month, mode, user_token)

    db.session.add(trip)
    db.session.commit()

    response = trip_schema.dump(trip)
    return jsonify(response) 