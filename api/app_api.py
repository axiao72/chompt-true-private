from fastapi import Body, FastAPI
from pydantic import BaseModel
from typing import Optional
from typing import Annotated
import pymongo
import time
from datetime import datetime
from src.resy_util import *
from src.mongo_util import *
from src.llm_util import *
from api.pydantic_models import *


app = FastAPI()

EMBED_MODEL = instantiate_embed_model("intfloat/e5-large-v2", 'HF')


@app.post("/api/chat")
def chat(vision: IdealMeal):   
    # Connect to Mongo
    DB = connect_to_mongo()
    mongo_reviews = DB["reviews"]
    # mongo_reviews = DB["chunked_reviews"]
    # vision_dict = vision.model_dump()
    print(f"Getting recommendations for the query: '{vision.description}'....", file=sys.stderr)
    # Extract cuisine and neighborhood for metadata filter
    # pre_metadata_filters, post_metadata_filters = extract_entities(vision.description, os.getenv('OPENAI_API_KEY'))
    pre_metadata_filters, post_metadata_filters = {'$and': []}, {} # Searching on little chunks, point is to not need explicit filters
    print(f"Got post search filters: {post_metadata_filters}")
    if vision.res_mode_on:
        print("Reservation mode on.")
        pre_metadata_filters['$and'].append(
            {
                'hasResy': True
            }
        )
        post_metadata_filters['hasResy'] = True
        # Post-filter search
        resto_recs, used_reservations, used_neighborhood_and_cuisine, used_neighborhood, used_cuisine = get_recs_mongo_res_mode(vision, EMBED_MODEL, mongo_reviews, post_metadata_filters)
    else:
        print("Reservation mode off.")
        used_reservations = False
        resto_recs, used_neighborhood_and_cuisine, used_neighborhood, used_cuisine = get_recs_mongo_non_res_mode(vision, EMBED_MODEL, mongo_reviews, post_metadata_filters) 
    print(f"Broncos Country... Let's Ride!!!", file=sys.stderr)
    print(f"Got {len(resto_recs)} recs.", file=sys.stderr)
    # Insert recommended restaurants into Mongo
    mongo_recs = DB["recommendations"]
    insert_recs = {
        'date': datetime.today().strftime('%Y-%m-%d'),
        'user_input': vision.description,
        'reservation_mode': vision.res_mode_on
    }
    restos_list = []        
    for count, rec in enumerate(resto_recs):
        # print(f"Returned rec #{count}: \n{rec}")
        insert_recs[f'restaurant{count+1}_name'] = rec['resto_name']
        insert_recs[f'restaurant{count+1}_score'] = rec['score']
        restos_list.append({
            'resto_name': rec['resto_name'],
            'review': rec['text'],
            'perfect_for': rec['perfect_for_tags'],
            'price_range': rec['price_range'],
            'image_url': rec['image_url'],
            'website': rec['resto_website'],
            'neighborhood': rec['neighborhood'].title()
        })
        if 'resy_venue_url' in rec:
            if vision.res_mode_on:
                restos_list[count]['resy_url'] = rec['resy_venue_url'].replace('<party_size>', f'{vision.party_size}').replace('<res_date>', f'{vision.res_date}') + f'&time={vision.res_time.replace(":", "")}'
            else:
                restos_list[count]['resy_url'] = rec['resy_venue_url']
        # print(f"Final rec formatted for UI: \n{restos_list[count]}")
    
    try:
        insert_result = mongo_recs.insert_one(insert_recs)
        print(f"Inserted recommendation to Mongo: {insert_result}")
    except pymongo.errors.OperationFailure:
        print("An authentication error was received. Are you sure your database user is authorized to perform write operations?")
    
    top_rec = restos_list[0]
    pitch = query_llm(restaurant_name=top_rec['resto_name'], review=top_rec['review'], vision=vision.description, openai_api_key=os.getenv('OPENAI_API_KEY'))
    # print(restos_list)
    if not used_reservations:
        print("Did NOT use reservation data for recs!", file=sys.stderr)
    else:
        print("DID use reservation data for recs!!", file=sys.stderr)
    return {
        'restos': restos_list,
        'usedReservations': used_reservations,
        'usedBoth': used_neighborhood_and_cuisine,
        'usedNeighborhood': used_neighborhood,
        'usedCuisine': used_cuisine,
        'pitch': pitch
    }

