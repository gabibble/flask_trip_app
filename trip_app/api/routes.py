from flask import Blueprint, request, jsonify 
from trip_app.models import db, Trip, trip_schema, trips_schema
from trip_app.helpers import token_required

api = Blueprint('api', __name__, url_prefix = '/api')

@api.route('/getdata')
@token_required
def getdata(user_token):
    return{'token': user_token}


@api.route('/create_trip', methods = ['POST'])
@token_required
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
    user_token = current_user_token

    trip = Trip(name, descrip, origin, dest, guests, nights, accom, month, mode, user_token=user_token)

    db.session.add(trip)
    db.session.commit()

    response = trip_schema.dump(trip)
    return jsonify(response) 

#GET ALL TRIPS
@api.route('/get_trip/<id>', methods = ['GET'])
@token_required
def get_trip(current_user_token, id):
    owner = current_user_token
    if owner == current_user_token:
        trip = Trip.query.get(id)
        response = trip_schema.dump(trip)
        return jsonify(response)
    else: 
        return jsonify({'message': 'Token is Missing!'}), 401
    
#GET ONE TRIP
@api.route('/get_trips', methods = ['GET'])
@token_required
def get_trips(current_user_token):
    owner = current_user_token
    trips = Trip.query.filter_by(user_token = owner).all()
    response = trips_schema.dump(trips)
    return jsonify(response)


#UPDATE TRIP
@api.route('/update_trip/<id>', methods = ['POST', 'PUT'])
@token_required
def update_trip(current_user_token, id):
    
    trip = Trip.query.get(id)

    trip.name = request.json['name']
    trip.descrip = request.json['descrip']
    trip.origin = request.json['origin']
    trip.dest = request.json['dest']
    trip.guests = request.json['guests']
    trip.nights = request.json['nights']
    trip.accom = request.json['accom']
    trip.month = request.json['month']
    trip.mode = request.json['mode']
    trip.user_token = current_user_token
    
    db.session.commit()
    response = trip_schema.dump(trip)
    return jsonify(response)




@api.route('/del_trip/<id>', methods = ['DELETE'])
@token_required
def delete_trip(current_user_token, id):
    trip = Trip.query.get(id)
    db.session.delete(trip)
    db.session.commit()
    response = trip_schema.dump(trip)
    return jsonify(response)