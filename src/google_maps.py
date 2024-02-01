import json
import googlemaps
from pprint import pprint
import pymongo
from tqdm.auto import tqdm
import os


def get_gmaps_client():
    print(os.environ.get('GOOGLE_API_KEY'))
    google_api_key = os.environ.get('GOOGLE_API_KEY')
    gmaps = googlemaps.Client(key=google_api_key)
    return gmaps


def get_geo_distances(restos: dict, query_origin: str, gmaps):
    """
    Calculates the distance of each restaurant candidate from the user's specified origin using Google's Maps API.

    Parameters:
    - restos (dict): A dict of restaurants with all the fields from Mongo.
    - query_origin (str): Location extracted from the user's input query, aka where they are looking for a restaurant.
    - gmaps: Google Maps API Client

    Returns:
    list: Dictionary of restos with each resto's distance (in miles) from the query origin appended to its dictionary entry.
    """
    origins = [query_origin]
    destinations = [{"lat": resto['geo']['latitude'], "lng": resto['geo']['longitude']} for resto in restos]
    destination_batches = [destinations[i:i+25] for i in range(0, len(destinations), 25)]

    final_distances = []
    for destinations in destination_batches:
        result_distances = gmaps.distance_matrix(
            origins, 
            destinations, 
            mode="walking",
            units='imperial'
        )
        final_distances.extend(result_distances['rows'][0]['elements'])
    for idx, resto in enumerate(restos):
        resto['distance_to_origin'] = float(final_distances[idx]['distance']['text'].split(' mi')[0])

    return restos
    


try:
    MONGO_CLIENT = pymongo.MongoClient("mongodb+srv://axiao72:McSplash7013$@chomptcluster.k5sqjpd.mongodb.net/?retryWrites=true&w=majority")
    DB = MONGO_CLIENT.chompt
    print("Connected to Mongo!")
except pymongo.errors.ConfigurationError:
    print("Invalid URI host, confirm Atlas host name and password is correct in the connection string!")
mongo_reviews = DB['reviews']

restos = list(mongo_reviews.find({'neighborhood': 'east village'}))[0:50]
restos_w_distance = get_geo_distances(restos, 'penn station new york', get_gmaps_client())
for resto in restos_w_distance:
    print(f"{resto['resto_name']}: {resto['distance_to_origin']}")

