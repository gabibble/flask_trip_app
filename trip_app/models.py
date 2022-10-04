#ORM transfers flask class models to pgadmin tables
from flask_sqlalchemy import SQLAlchemy

#sends models to db as tables
from flask_migrate import Migrate

#create tokens
import secrets 

#imports for flask marshmelllow 
from flask_marshmallow import Marshmallow

#handles third party api calls
from trip_app.api_helpers import *

db = SQLAlchemy()
ma = Marshmallow()

class Trip(db.Model):
    id = db.Column(db.String, primary_key = True)
    #coming from user input in React App
    name = db.Column(db.String(150))
    descrip = db.Column(db.String, nullable = True)
    origin = db.Column(db.String(150))
    dest = db.Column(db.String(150))
    guests = db.Column(db.Integer)
    nights = db.Column(db.Integer) 
    accom = db.Column(db.String(150))
    month = db.Column(db.Integer)
    mode = db.Column(db.String(150))
    # coming from geo helpers
    origcity = db.Column(db.String(150))
    destcity = db.Column(db.String(150))
    destcountry = db.Column(db.String(150))
    # coming from travel info function in apihelpers
    distance = db.Column(db.Integer)
    duration = db.Column(db.Numeric(precision=10, scale=1))
    travcost = db.Column(db.Numeric(precision=10, scale=2))
    # coming from weather info function in apihelpers
    tavg = db.Column(db.Integer)
    tmin = db.Column(db.Integer)
    tmax = db.Column(db.Integer)
    prcp = db.Column(db.Numeric(precision=10, scale=1))
    temps = db.Column(db.String(200))
    prcps = db.Column(db.String(300))
    #coming from get pic function in apihelpers
    photo = db.Column(db.String, nullable = True) #long string
    photolink = db.Column(db.String, nullable = True)
    accomcost = db.Column(db.Numeric(precision=10, scale=2))
    totalcost = db.Column(db.Numeric(precision=10, scale=2))
    user_token = db.Column(db.String, nullable=False)

    def __init__(self, name, descrip, origin, dest, guests, nights, accom, month, mode, user_token, id=""):
        self.id = self.set_id()
        self.name = name
        self.descrip = descrip
        self.origin = origin
        self.dest = dest
        self.guests = guests
        self.nights = nights
        self.accom = accom
        self.month = month
        self.mode = mode
        self.origcity = cityname(self.origin)
        self.destcity = cityname(self.dest)
        self.destcountry = country(geo(self.dest))
        self.travelinfo = get_travelinfo(self.origin, self.dest, self.mode, self.guests)
        self.distance = self.travelinfo['distance']
        self.duration = self.travelinfo['duration']
        self.travcost = self.travelinfo['travcost']
        self.weatherinfo = get_weather(self.destcity, self.month)
        self.tavg = self.weatherinfo['tavg']
        self.tmin = self.weatherinfo['tmin']
        self.tmax = self.weatherinfo['tmax']
        self.prcp = self.weatherinfo['prcp']
        self.temps = self.weatherinfo['temps']
        self.prcps = self.weatherinfo['prcps']
        self.photoinfo = get_pic(self.destcity)
        self.photo = self.photoinfo['url']
        self.photolink = self.photoinfo['credit']
        self.accomcost = self.get_accomcost()
        self.totalcost = self.accomcost + self.travcost
        self.user_token = user_token

        
    def get_accomcost(self):
        """calculates accomodation cost based on accom type, number of guests, and number of nights"""
        if self.accom.lower() == 'hotel':
            # assuming 2 huests will share a room  
            # https://www.statista.com/statistics/195704/average-hotel-room-rate-in-the-us-since-2005/
            return 125 * (int(self.guests) + 1)//2 * (int(self.nights))
        elif self.accom.lower() == 'airbnb entire house':
            # https://www.alltherooms.com/analytics/average-airbnb-prices-by-city/
            if self.destcountry == "United States":
                return 216 * (int(self.guests) + 1)//2 * (int(self.nights))
            else:
                return 137 * (int(self.guests) + 1)//2 * (int(self.nights))
        elif self.accom.lower() == 'airbnb private room':
            return 66 * (int(self.guests) + 1)//2 * (int(self.nights))
        elif self.accom.lower() == 'campground':
            # https://www.letstravelfamily.com/average-cost-of-camping/#:~:text=Camping%20fees%20in%20National%20Parks,able%20to%20accommodate%2040%20pax.
            # assuming 4 people per campsite
            return 20 * (int(self.guests) + 3)//4 * (int(self.nights))

    def __repr__(self):
        return f"The following trip has been added: {self.name}"

    def set_id(self):
        return secrets.token_urlsafe()
    
#helps data go to insomnia
class TripSchema(ma.Schema):
    class Meta:
        fields = ['id', 'name' 'descrip', 'origin', 'dest', 'guests', 'nights', 'accom', 'month', 'mode', 'origcity', 'destcity', 'destcountry', 'distance', 'duration', 'travcost', 'tavg', 'tmin', 'tmax', 'prcp', 'temps', 'prcps', 'photo', 'photolink', 'accomcost', 'totalcost']

trip_schema = TripSchema()
trips_schema = TripSchema(many = True)