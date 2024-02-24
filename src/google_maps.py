import json
import googlemaps
from pprint import pprint
import pymongo
from tqdm.auto import tqdm
import os
from src.google_util import *
    

# Testing code
try:
    MONGO_CLIENT = pymongo.MongoClient("mongodb+srv://axiao72:McSplash7013$@chomptcluster.k5sqjpd.mongodb.net/?retryWrites=true&w=majority")
    DB = MONGO_CLIENT.chompt
    print("Connected to Mongo!")
except pymongo.errors.ConfigurationError:
    print("Invalid URI host, confirm Atlas host name and password is correct in the connection string!")
mongo_reviews = DB['reviews']

restos = list(mongo_reviews.find({'neighborhood': 'east village'}))[0:3]
restos_w_distance = get_geo_distances(restos, 'penn station new york', get_gmaps_client())
for resto in restos_w_distance:
    pprint(resto)
    print(f"\n\n{resto['resto_name']}: {resto['distance_to_origin']}")

