import requests
from geopy.geocoders import Nominatim
from geopy.distance import geodesic
import requests_cache

from trip_app.cities import cities
from trip_app.photocache import photos

from api_keys import * 
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
    location = geolocator.reverse(loc)
    city=location.raw['address']['city']
    return city

def state(loc):
    location = geolocator.reverse(loc)
    state=location.raw['address']['state']
    return state

def country(loc):
    location = geolocator.reverse(loc)
    country=location.raw['address']['country']
    return country

def get_travelinfo(origin, dest, mode, guests):
    if mode == "car":
        url = "https://trueway-matrix.p.rapidapi.com/CalculateDrivingMatrix"
        querystring = {"origins":f"{geo(origin)};","destinations":f"{geo(dest)};"}
        headers = {
            "X-RapidAPI-Key": rapid_api,
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
            "X-RapidAPI-Key": rapid_api,
            "X-RapidAPI-Host": "meteostat.p.rapidapi.com"
        }
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            data = response.json()['data']
            print(data)
        else:
            print('unable to get weather data')
            return False
    tavg = int(data[month]['tavg'])
    tmin = int(data[month]['tmin'])
    tmax = int(data[month]['tmax'])
    prcp = int(data[month]['prcp'])
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
        url = f"https://api.unsplash.com/search/photos?query={loc}&client_id={unsplash_access_key}"
        response = requests.get(url)
        # print(url)
        if response.status_code == 200:
            data = response.json()['results'][0]
        photo_url = data['urls']['regular']
        photo_credit = data['links']['html']
        photographer_name = data['user']['name']
        photographer_link = data['user']['links']['html']
        return{'url':photo_url, 'credit':photo_credit, 'photographer_name': photographer_name,'photographer_link': photographer_link,}
            







# {"meta":{"generated": "2022-09-29 23:04:55", "stations": ["72698", "KVUO0", "72694", "72791"]},
# "data":[
#     {"month":1,"tavg":41.5,"tmin":36.1,"tmax":46.9,"prcp":5.039,"wspd":9.1,"pres":1019.2,"tsun":null},
#     {"month":2,"tavg":43.9,"tmin":36.9,"tmax":50.9,"prcp":3.693,"wspd":8.4,"pres":1017.9,"tsun":null},
#     {"month":3,"tavg":47.9,"tmin":39.7,"tmax":56.1,"prcp":3.98,"wspd":7.5,"pres":1017.6,"tsun":null},
#     {"month":4,"tavg":52.6,"tmin":43.7,"tmax":61.5,"prcp":2.945,"wspd":7.0,"pres":1018.1,"tsun":null},{"month":5,"tavg":59.2,"tmin":49.6,"tmax":68.7,"prcp":2.551,"wspd":6.5,"pres":1017.4,"tsun":null},{"month":6,"tavg":64.0,"tmin":54.1,"tmax":73.8,"prcp":1.63,"wspd":6.7,"pres":1017.3,"tsun":null},{"month":7,"tavg":70.0,"tmin":58.6,"tmax":81.3,"prcp":0.508,"wspd":7.0,"pres":1017.1,"tsun":null},{"month":8,"tavg":70.4,"tmin":59.0,"tmax":81.9,"prcp":0.551,"wspd":6.5,"pres":1016.3,"tsun":null},{"month":9,"tavg":65.2,"tmin":54.3,"tmax":76.1,"prcp":1.524,"wspd":6.0,"pres":1016.4,"tsun":null},{"month":10,"tavg":55.4,"tmin":46.9,"tmax":63.9,"prcp":3.425,"wspd":6.2,"pres":1018.4,"tsun":null},{"month":11,"tavg":46.8,"tmin":40.8,"tmax":52.9,"prcp":5.417,"wspd":7.8,"pres":1018.9,"tsun":null},{"month":12,"tavg":41.2,"tmin":36.3,"tmax":46.2,"prcp":5.72,"wspd":9.1,"pres":1018.9,"tsun":null}]}