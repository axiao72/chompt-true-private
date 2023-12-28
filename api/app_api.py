from fastapi import Body, FastAPI
from pydantic import BaseModel
from typing import Optional
from typing import Annotated
import pymongo
import time
from datetime import datetime
from src.py_ai_util import *
from api.pydantic_models import *


app = FastAPI()

EMBED_MODEL = instantiate_embed_model("intfloat/e5-large-v2", 'HF')

# Connect to Mongo
try:
    MONGO_CLIENT = pymongo.MongoClient("mongodb+srv://axiao72:McSplash7013$@chomptcluster.k5sqjpd.mongodb.net/?retryWrites=true&w=majority")
    DB = MONGO_CLIENT.chompt
    print("Connected to Mongo!")
except pymongo.errors.ConfigurationError:
    print("Invalid URI host, confirm Atlas host name and password is correct in the connection string!")


@app.post("/api/chat")
def chat(vision: IdealMeal):   
    mongo_reviews = DB["reviews"]
    # vision_dict = vision.model_dump()
    print(f"Getting recommendations for the query: '{vision.description}'....", file=sys.stderr)
    # Extract cuisine and neighborhood for metadata filter
    metadata_filters = extract_entities(vision.description, os.getenv('OPENAI_API_KEY'))
    if vision.res_mode_on:
        # print("Reservation mode on! Getting all available reservations under user's critera from Resy...")
        # # Get all restaurants with available resy reservations under user's specified res criteria
        # available_venues = get_available_resy_venues(vision.res_date, vision.res_time, vision.party_size)
        # # Add available resy venues to metadata filter if there were any available restaurants matching user's criteria
        # if available_venues:   
        #     print(f"Found available reservations matching user's criteria! Adding to metadata filter.")
        #     metadata_filters['$and'].append(
        #         {
        #             'resy_venue_id':{"$in": [venue['resy_id'] for venue in available_venues]}
        #         }
        #     )
        # Current Approach: Just add resy_venue_url $exists filter to only get Resy-capable restaurants, 
        # then check Resy through search api for each restaurant that's returned from candidate generation until you get to 3 or exhaust all candidates
        print("Reservation mode on. Applying resy_venue_id exists filter.")
        metadata_filters['$and'].append(
            {
                'hasResy': True
            }
        )
    else:
        print("Reservation mode off.")
    # Get recommendations (trying candidate generation now)
    # Candidate Generation
    resto_recs, used_reservations = get_top_restos_mongo(
        vision=vision,
        embed_model=EMBED_MODEL, 
        mongo_reviews=mongo_reviews,
        metadata_filters=metadata_filters
    )
    print(f"Broncos Country... Let's Ride!!!", file=sys.stderr)
    print(f"Got {len(resto_recs)} recs.", file=sys.stderr)
    # Insert recommended restaurants into Mongo
    mongo_recs = DB["recommendations"]
    insert_recs = {
        'date': datetime.today().strftime('%Y-%m-%d'),
        'user_input': vision.description,
        'reservation_mode': vision.res_mode_on
    }
    # (Don't need to do this with Mongo) Get just the review and metadata, without the sim search score
    # resto_recs_wo_score = [i['metadata'] for i in resto_recs]
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
        'pitch': pitch
    }

