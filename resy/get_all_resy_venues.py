import json
import requests
import re
from datetime import datetime
from tqdm.auto import tqdm
import random
import time

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
resy_venues = []
# Iterate through all Resy pages (maximum 20 pages with 50 hits per page, 1000 total)
for page_cnt in tqdm(range(1, 21)):
    data = {
        'geo': {'latitude': 40.712941, 'longitude': -74.006393, 'radius': 35420},
        'page': page_cnt,
        'per_page': 50,
        'query': '',
        'slot_filter': {'day': current_date, 'party_size': party_size},
        'types': ['venue']
    }
    response = requests.post(
        url,
        data=json.dumps(data),
        headers=headers
    )
    if response.status_code == 200:
        print(f"Got response for page {page_cnt}")
        resy_json = json.loads(response.text)
        resy_search_results = resy_json['search']['hits']
        for hit in resy_search_results:
            resy_venue_name = hit['name']
            resy_venue_id = hit['id']['resy']
            resy_venue_url = f"https://widgets.resy.com/?venueId={resy_venue_id}#/venues/{resy_venue_id}?seats=<party_size>&date=<res_date>"
            resy_venues.append(
                {
                    'resy_venue_name': resy_venue_name,
                    'resy_venue_id': resy_venue_id,
                    'resy_venue_url': resy_venue_url
                }
            )
        print(f"Added venue info for page {page_cnt}")
    else:
        print(f"Error while pinging resy for page {page_cnt}: {response.status_code}. Exiting.\n")
        break
    sleep_time = random.randint(1, 3)
    print(f"Sleeping for {sleep_time} secs.... Let... Him.. Cook.")
    time.sleep(sleep_time)

with open('all_resy_venues.json', 'wb') as file:
    json.dump(resy_venues, file)
    