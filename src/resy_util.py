import json
import requests
import os
import sys
from tqdm.auto import tqdm
import random
import time


def get_resy_search_headers():
    resy_api_key = os.environ.get('RESY_API_KEY')
    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json, text/plain, */*',
        'Authorization': f'ResyAPI api_key="{resy_api_key}"',
        'X-Resy-Auth-Token': os.environ.get('RESY_AUTH_TOKEN'),
        'X-Resy-Universal-Auth': os.environ.get('RESY_UNIVERSAL_AUTH'),
        'X-Origin': 'https://resy.com',
        'Origin': 'https://resy.com',
        'Referer': 'https://resy.com',
        'Sec-Fetch-Dest': 'empty',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Mode': 'same-site'
    }
    return headers


def get_available_resy_venues(res_date: str, res_time: str, party_size: int):
    # Resy search API
    url = 'https://api.resy.com/3/venuesearch/search'
    available_venues = []
    # Construct availability search parameters with user's specified filters
    data = {
            'availability': True,
            'order_by': 'availability',
            'geo': {'latitude': 40.712941, 'longitude': -74.006393, 'radius': 35420},
            # 'page': 1,
            'per_page': 50,
            'query': '',
            'slot_filter': {'day': res_date, 'party_size': party_size, 'time_filter': res_time},
            'types': ['venue']
        }
    headers = get_resy_search_headers()
    # Loop through all 20 pages of Resy search api (the API maxes out at 1000 total hits, 20 pages with 50 hits per page)
    for page_nbr in tqdm(range(1,21)):
        print(f"Getting available Resy reservations on page {page_nbr}...")
        data['page'] = page_nbr
        response = requests.post(
            url,
            data=json.dumps(data),
            headers=headers
        )
        # Check if the request was successful (status code 200)
        if response.status_code == 200:
            # Add venues if they have available slots
            resy_json = json.loads(response.text)
            resy_search_results = resy_json['search']['hits']
            # Loop through each search hit to check if they actually have available slots
            for i in resy_search_results:
                if len(i['availability']['slots']) > 0:
                    available_venues.append({
                        'name': i['name'],
                        'resy_id': i['id']['resy'],
                        'open_slots': [slot['date'] for slot in i['availability']['slots']]
                    })
            print(f"Got available Resy reservations on page {page_nbr}!")
        else:
            print(f"Error: {response.status_code}")
        if page_nbr == 10:
            sleep_time = random.randint(1, 3)
            print(f"Sleeping for {sleep_time} secs.... Let... Him.. Cook.")
            time.sleep(sleep_time)
    print(f"Got all venues with available reservations on {res_date} at {res_time} for {party_size}. Let's Ride.")
    return available_venues


def get_top_available_candidates(candidates: list, res_date: str, res_time: str, party_size: int):
    available_candidates = []
    url = 'https://api.resy.com/3/venuesearch/search'
    data = {
        'geo': {'latitude': 40.712941, 'longitude': -74.006393, 'radius': 35420},
        'availability': True,
        'order_by': 'availability',
        'page': 1,
        'per_page': 50,
        'query': '',
        'slot_filter': {'day': res_date, 'time_filter': res_time, 'party_size': party_size},
        'types': ['venue']
    }
    headers = get_resy_search_headers()
    # Loop through candidates until find 3 available on Resy or exhaust all candidates
    i = 0
    print(f"{len(candidates)} candidates.", file=sys.stderr)
    while i < len(candidates):
        cand = candidates[i]
        print(f"Checking candidate #{i+1} {cand['resy_venue_name']} availability", file=sys.stderr)
        data['query'] = cand['resy_venue_name']
        response = requests.post(
            url,
            data=json.dumps(data),
            headers=headers
        )
        if response.status_code == 200:
            resy_json = json.loads(response.text)
            if resy_json['search']['hits'] and (len(resy_json['search']['hits'][0]['availability']['slots'])) > 0:
                available_candidates.append(cand)
                print(f"Found available candidate! Candidate #{i+1}", file=sys.stderr)
        else:
            print(f"Error: {response.status_code}")
        i += 1
        sleep_time = random.randint(1, 3)
        print(f"Sleeping for {sleep_time} secs.... Let... Him.. Cook.", file=sys.stderr)
        time.sleep(sleep_time)
    print(f"Returning {len(available_candidates)} final candidates.", file=sys.stderr)
    return available_candidates