import pymongo
from urllib.request import urlopen
import json
import requests
import re
from datetime import datetime
from tqdm.auto import tqdm
import random
import time


def construct_resy_query_with_neighborhood(resto_name: str, neighborhood: str, day: str, party_size: int):
    # resto_name_str = resto_name.split(' ') + [neighborhood]
    # resy_venue_str = '%20'.join(resto_name_str)
    resy_venue_str = resto_name + ' ' + neighborhood
    data = {
        # 'availability': True,
        # 'order_by': 'availability',
        'geo': {'latitude': 40.712941, 'longitude': -74.006393, 'radius': 35420},
        'page': 1,
        'per_page': 50,
        'query': resy_venue_str,
        'slot_filter': {
            'day': day, 
            'party_size': party_size 
        },
        'types': ['venue']
    }
        
    return data
        
def construct_resy_query_without_neighborhood(resto_name: str, day: str, party_size: int):
    # resto_name_str = resto_name.split(' ')
    # resy_venue_str = '%20'.join(resto_name_str)
    data = {
        # 'availability': True,
        # 'order_by': 'availability',
        'geo': {'latitude': 40.712941, 'longitude': -74.006393, 'radius': 35420},
        'page': 1,
        'per_page': 50,
        'query': resto_name,
        'slot_filter': {
            'day': day, 
            'party_size': party_size 
        },
        'types': ['venue']
    }
        
    return data


# Connect to Mongo
try:
    client = pymongo.MongoClient("mongodb+srv://axiao72:McSplash7013$@chomptcluster.k5sqjpd.mongodb.net/?retryWrites=true&w=majority")
    print("Connected to Mongo!")
except pymongo.errors.ConfigurationError:
    print("Invalid URI host, confirm Atlas host name and password is correct in the connection string!")

# Connect to Chompt db and reviews collection
db = client.chompt 
mongo_reviews = db["reviews"]
# *** CAREFUL!!! Make sure you want to unset
mongo_reviews.update_many({}, {'$unset': {"resy_venue_id": "", "resy_venue_name": "", "resy_venue_url": ""}})
mongo_reviews.update_many({}, {'$set': {"hasResy": False}})

# Resy API authorization headers
authorization = 'ResyAPI api_key="VbWk7s3L4KiK5fzlO7JD3Q5EYolJI7n5"'
x_resy_auth_token = 'eyJ0eXAiOiJKV1QiLCJhbGciOiJFUzI1NiJ9.eyJleHAiOjE3MDY1NzIwODQsInVpZCI6NzA3ODk1NiwiZ3QiOiJjb25zdW1lciIsImdzIjpbXSwibGFuZyI6ImVuLXVzIiwiZXh0cmEiOnsiZ3Vlc3RfaWQiOjMxODEzMDE2fX0.AD5AkQKMGhytKFsajCqS9u1UstINY8yjvZfoIO3QeQ6l7NmVRvTibfKjXsCVBFeV_tQ_mfM1Vz56TatGoGZ1ZRkyAcquAvudt72HDsafErO_esHsHK9-Z6GT1TmagmsL6xca7sgGkvtwqiPsQ7124ne_WeGVQJxBNXu_WecA8RoAkcMX'
x_resy_universal_auth = 'eyJ0eXAiOiJKV1QiLCJhbGciOiJFUzI1NiJ9.eyJleHAiOjE3MDY1NzIwODQsInVpZCI6NzA3ODk1NiwiZ3QiOiJjb25zdW1lciIsImdzIjpbXSwibGFuZyI6ImVuLXVzIiwiZXh0cmEiOnsiZ3Vlc3RfaWQiOjMxODEzMDE2fX0.AD5AkQKMGhytKFsajCqS9u1UstINY8yjvZfoIO3QeQ6l7NmVRvTibfKjXsCVBFeV_tQ_mfM1Vz56TatGoGZ1ZRkyAcquAvudt72HDsafErO_esHsHK9-Z6GT1TmagmsL6xca7sgGkvtwqiPsQ7124ne_WeGVQJxBNXu_WecA8RoAkcMX'
# Resy Search API
url = 'https://api.resy.com/3/venuesearch/search'
# Full Resy Search API request headers
headers = {
    'Content-Type': 'application/json',
    'Accept': 'application/json, text/plain, */*',
    'Authorization': authorization,
    'X-Resy-Auth-Token': x_resy_auth_token,
    'X-Resy-Universal-Auth': x_resy_universal_auth,
    'X-Origin': 'https://resy.com',
    'Origin': 'https://resy.com',
    'Referer': 'https://resy.com',
    'Sec-Fetch-Dest': 'empty',
    'Sec-Fetch-Mode': 'cors',
    'Sec-Fetch-Mode': 'same-site'
    
}

current_date = datetime.today().strftime('%Y-%m-%d')
# date needs to be in "YYYY-MM-DD" format
res_date = current_date
party_size = 2
resy_counter = 0
# Get mongo documents that don't already have a Resy link
mongo_docs = list(mongo_reviews.find({"hasResy": False}))
print(f"Got {len(mongo_docs)} documents from Mongo. Cheffing up Resy data now...")
for doc in tqdm(mongo_docs):
    name = doc['resto_name']
    neighborhood = doc['neighborhood']
    print(f"***** Getting Resy info for {name} at the {neighborhood} location *****\n")
    # Check if Mongo has multiple documents with the restaurant name. If it does, add neighborhood to the query.
    docs_w_name = list(mongo_reviews.find({"resto_name": name}))
    if len(docs_w_name) > 1:
        print(f"{name} has multiple Infatuation Mongo docs. Searching with name and neighborhood combined...")
        using_neighborhood = "Yes"
        data = construct_resy_query_with_neighborhood(resto_name=name, 
                                           neighborhood=neighborhood, 
                                           day=res_date, 
                                           party_size=party_size)
    else:
        print(f"{name} has 1 Infatuation Mongo doc. Searching with just name...")
        using_neighborhood = "No"
        data = construct_resy_query_without_neighborhood(resto_name=name, 
                                           day=res_date, 
                                           party_size=party_size)
    
    response = requests.post(
        url,
        data=json.dumps(data),
        headers=headers
    )
    resy_search_results = []
    if response.status_code == 200:
        resy_json = json.loads(response.text)
        resy_search_results = resy_json['search']['hits']
    else:
        print(f"Error while pinging resy for {name}: {response.status_code}. Moving to next restaurant\n")
        continue
    if resy_search_results:
        print(f"Received results from Resy! Used neighborhood in query? {using_neighborhood}\n")
        # Take the first result
        hit = resy_search_results[0]
        resy_venue_id = hit['id']['resy']
        resy_venue_name = hit['name']
        resy_venue_url = f"https://widgets.resy.com/?venueId={resy_venue_id}#/venues/{resy_venue_id}?seats=<party_size>&date=<res_date>"
        # Could update using _id as the filter? Not sure how it works with the autogenerated Object field
        mongo_reviews.update_many(
            {"resto_name": name, "neighborhood": neighborhood},
            {"$set": {
                "resy_venue_id": resy_venue_id, 
                "resy_venue_name": resy_venue_name, 
                "resy_venue_url": resy_venue_url,
                "hasResy": True
            }}
        )
        print(f"Added: \n{resy_venue_id}, \n{resy_venue_name}, \n{resy_venue_url} \nto {name} in {neighborhood} Mongo document.")
        resy_counter += 1
        print(f"Cheffed up Resy data for {resy_counter} Infatuation restaurants so far.")
    else:
        print(f"No resy results for {name} in {neighborhood} Mongo document, with or without neighborhood query :(\n")
    
    sleep_time = random.randint(1, 3)
    print(f"Sleeping for {sleep_time} secs.... Let... Him.. Cook.")
    time.sleep(sleep_time)
        
    

