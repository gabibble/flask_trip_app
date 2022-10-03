import requests
import os
from geopy.geocoders import Nominatim
from geopy.distance import geodesic
import requests_cache

from trip_app.cities import cities
from trip_app.photocache import photos

geolocator = Nominatim(user_agent="trip app")
requests_cache.install_cache(cache_name='tripdata_cache', backend='sqlite', expire_after=180)


def geo(loc):
    location = geolocator.geocode(loc)
    return f"{location.latitude}, {location.longitude}"

def lat(loc):
    location = geolocator.geocode(loc)
    return location.latitude

def lon(loc):
    location = geolocator.geocode(loc)
    return location.longitude

def cityname(loc):
    location = geolocator.reverse(loc, language="en")
    city=location.raw['address']['city']
    return city

def state(loc):
    location = geolocator.reverse(loc, language="en")
    state=location.raw['address']['state']
    return state

def country(loc):
    location = geolocator.reverse(loc, language="en")
    country=location.raw['address']['country']
    return country

def get_travelinfo(origin, dest, mode, guests):
    if mode == "car":
        url = "https://trueway-matrix.p.rapidapi.com/CalculateDrivingMatrix"
        querystring = {"origins":f"{geo(origin)};","destinations":f"{geo(dest)};"}
        headers = {
            "X-RapidAPI-Key": os.environ.get('rapid_api'),
            "X-RapidAPI-Host": "trueway-matrix.p.rapidapi.com"
        }
        response = requests.get(url, headers=headers, params=querystring)
        if response.status_code == 200:
            print('collecting data from trueway matrix')
            data = response.json()
            if data['distances'][0][0] != None:
                dist = int(data['distances'][0][0] * 0.000621371)
                dur = data['durations'][0][0] / 3600
            else:
                dist =int(geodesic(geo(origin), geo(dest)).miles)
                dur = geodesic(geo(origin), geo(dest)).miles / 60
                print('no driving gata. consider switching mode to plane')
        else:
            dist =int(geodesic(geo(origin), geo(dest)).miles)
            dur = geodesic(geo(origin), geo(dest)).miles / 60
            print('error in API: driving data calculated based on geodesic distance and avg speed of 60mph')
        #per diem milaege rate https://www.gsa.gov/travel/plan-book/transportation-airfare-pov-etc/privately-owned-vehicle-pov-mileage-reimbursement-rates
        cost = dist * .22 * 2
        return {'distance': dist, 'duration': dur, 'travcost': int(cost)}

    else:
        dist = int(geodesic(geo(origin), geo(dest)).miles)
        dur = (geodesic(geo(origin), geo(dest)).miles / 465) + .5
        #flight cost calculation https://www.transportation.gov/sites/dot.gov/files/2022-08/SIFL_Appendix_B_2022q1q2.pdf
        if dist <= 500:
            cost = ((dist * .2417) + 44) * 2 * int(guests)
        if dist > 500 and dist < 1500:
            cost = ((dist * .1843) + 44) * 2 * int(guests)
        else: 
            cost = ((dist * .1771) + 44) * 2 * int(guests)
        return {'distance': dist, 'duration': dur, 'travcost': int(cost)}

def get_weather(loc, month):
    month = int(month)
    if loc.lower() in cities:
        data = cities[loc.lower()]
    else:
        url = f"https://meteostat.p.rapidapi.com/point/normals?lat={lat(loc)}&lon={lon(loc)}&start=1991&end=2020&units=imperial"
        # querystring = {"lat":lat(loc),"lon":lon(loc),"start":"1991","end":"2020","units":"imperial"}
        headers = {
            "X-RapidAPI-Key": os.environ.get('rapid_api'),
            "X-RapidAPI-Host": "meteostat.p.rapidapi.com"
        }
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            data = response.json()['data']
        else:
            print('unable to get weather data')
            return {
                'tavg' : 0, 
                'tmin' : 0, 
                'tmax' : 0,
                'prcp' : 0,
                'temps' : "",
                'prcps' : ""
                }
    tavg = int(data[month]['tavg'])
    tmin = int(data[month]['tmin'])
    tmax = int(data[month]['tmax'])
    prcp = data[month]['prcp']
    temps = ','.join([str(int(month['tavg'])) for month in data])
    prcps = ','.join([str(month['prcp']) for month in data])
    return {
        'tavg' : tavg, 
        'tmin' : tmin, 
        'tmax' : tmax,
        'prcp' : prcp,
        'temps' : temps,
        'prcps' : prcps
        }

def get_pic(loc):
    if loc.lower() in photos.keys():
        return photos[loc.lower()]
    else:
        url = f"https://api.unsplash.com/search/photos?query={loc}&client_id={os.environ.get('unsplash_access_key')}"
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()['results'][0]
            photo_url = data['urls']['regular']
            photo_credit = data['links']['html']
            return{'url':photo_url, 'credit':photo_credit}
        else: 
            return{'url':f"https://source.unsplash.com/random?${loc}", 'credit':f"https://source.unsplash.com/random?${loc}"}

            



