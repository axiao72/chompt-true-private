from fastapi import Body, FastAPI, Response
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
from src.users import *
from src.helpers import *
from passlib.context import CryptContext
from passlib.hash import bcrypt
import requests
import uuid


app = FastAPI()

EMBED_MODEL = instantiate_embed_model("intfloat/e5-large-v2", 'HF')


@app.post("/api/signup")
async def signup(user: User, response: Response):
    try:
        new_user = await signup_user(user)
        # Generate uuid for session and add to session cookies
        generated_uuid = str(uuid.uuid4())
        print(f"Generated session uuid: {generated_uuid}", file=sys.stderr)
        response.set_cookie(key='session_uuid', value=generated_uuid)
        response.set_cookie(key='chompt_username', value=new_user['username'])
        session = await add_session(generated_uuid, new_user['username'])
        return {
            'username': new_user['username'],
            'firstName': new_user['firstName'],
            'lastName': new_user['lastName'],
            'inputs': new_user['inputs'],
            'resyClicks': new_user['resyClicks'],
            'success': True
        }
    except Exception as e:
        # Implement exception
        return {
            'success': False,
            'error': str(e)
        }


@app.post("/api/login")
async def login(credentials: LoginCredentials, response: Response):
    try:
        user = await login_user(credentials)
        print(f"User from app_api: {user}")
        # Generate uuid for session and add to session cookies
        generated_uuid = str(uuid.uuid4())
        print(f"Generated session uuid: {generated_uuid}", file=sys.stderr)
        response.set_cookie(key='session_uuid', value=generated_uuid)
        response.set_cookie(key='chompt_username', value=user['username'])
        session = await add_session(generated_uuid, user['username'])
        return {
            'username': user['username'],
            'firstName': user['firstName'],
            'lastName': user['lastName'],
            'inputs': user['inputs'],
            'resyClicks': user['resyClicks'],
            'success': True
        }
    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }


# Clears session UUID from cookies
@app.post("/api/logout")
async def logout(response: Response):
    try:
        response.delete_cookie(key='session_uuid')  
        response.delete_cookie(key='chompt_username')
        return {
            'success': True,
            'message': 'Cleared cookies!'
        }
    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }


@app.post("/api/get_mongo_user_by_username/{username}")
async def get_mongo_user_by_username(username: str):
    try:
        user = await find_user_by_username(username)
        return {
            'username': user['username'],
            'firstName': user['firstName'],
            'lastName': user['lastName'],
            'inputs': user['inputs'],
            'resyClicks': user['resyClicks'],
            'success': True
        }
    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }
    

@app.post("/api/get_mongo_user_from_uuid/{uuid}")
async def get_mongo_user_by_uuid(uuid: str):
    try:
        user_session = await find_user_by_uuid(uuid)
        user = await find_user_by_username(user_session['username'])
        return {
            'username': user['username'],
            'firstName': user['firstName'],
            'lastName': user['lastName'],
            'inputs': user['inputs'],
            'resyClicks': user['resyClicks'],
            'success': True
        }
    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }
    

@app.post("/api/track_event")
async def track_activity(event: Event):
    try:
        DB = connect_to_mongo()
        mongo_events = DB['events']
        event_data = dict(event)
        print(event_data, file=sys.stderr)
        mongo_events.insert_one(event_data)
        return {
            'success': True
        }
    except Exception as e:
        return {
            'success': False,
            'error': e
        }


@app.post("/api/chat")
def chat(vision: IdealMeal):  
    try: 
        # Connect to Mongo
        DB = connect_to_mongo()
        collection_name = "chunked_reviews"
        mongo_reviews = DB[collection_name]
        # mongo_reviews = DB["chunked_reviews"]
        # vision_dict = vision.model_dump()
        print(f"Getting recommendations in {vision.city} for the query: '{vision.description}'....", file=sys.stderr)
        # Extract cuisine and neighborhood for metadata filter. Keeping these as post filters just for extra layer of re-ranking/validation
        pre_metadata_filters, post_metadata_filters = extract_entities(vision.description, os.getenv('OPENAI_API_KEY'))
        # pre_metadata_filters, post_metadata_filters = {'$and': []}, {} # Searching on little chunks, point is to not need explicit filters
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
            resto_recs, used_reservations, used_neighborhood_and_cuisine, used_neighborhood, used_cuisine = get_recs_mongo_res_mode(vision, EMBED_MODEL, mongo_reviews, collection_name, post_metadata_filters)
        else:
            print("Reservation mode off.")
            used_reservations = False
            resto_recs, used_neighborhood_and_cuisine, used_neighborhood, used_cuisine = get_recs_mongo_non_res_mode(vision, EMBED_MODEL, mongo_reviews, collection_name, post_metadata_filters) 
        print(f"Broncos Country... Let's Ride!!!", file=sys.stderr)
        print(f"Got {len(resto_recs)} recs.", file=sys.stderr)
        # Insert recommended restaurants into Mongo
        mongo_recs = DB["recommendations"]
        insert_recs = {
            'username': vision.username,
            'date': datetime.today().strftime('%Y-%m-%d'),
            'user_input': vision.description,
            'reservation_mode': vision.res_mode_on
        }
        restos_list = []        
        full_reviews = DB['reviews']
        # For each rec, insert the name and score and get the full review from reviews collection
        for count, rec in enumerate(resto_recs):
            # print(f"Returned rec #{count}: \n{rec}")
            insert_recs[f'restaurant{count+1}_name'] = rec['resto_name']
            insert_recs[f'restaurant{count+1}_score'] = rec['score']
            print(f"Processing {rec['resto_name']} in {rec['neighborhood']}")
            # Get summarized review to display on frontend under each rec
            full_review_doc = list(full_reviews.find({
                                        'resto_name': rec['resto_name'].lower(), 
                                        'neighborhood': rec['neighborhood'],
                                        'review_date': rec['review_date'],
                                        'city': rec['city']
                                    }))
            # If-else in case we're in process of adding/generating more summaries
            if 'summarized_review' in full_review_doc[0]:
                full_review = full_review_doc[0]['summarized_review']
            else:
                full_review = full_review_doc[0]['text']
            # Get location data to format Maps url on frontend as well
            if 'geo' in full_review_doc[0]:
                full_address = full_review_doc[0]['geo']['fullAddress']
            else:
                full_address = ''
            # Add desired fields to return to frontend
            restos_list.append({
                'resto_name': capitalize_resto_name(rec['resto_name']),
                'review': full_review,
                'perfect_for': rec['perfect_for_tags'],
                'price_range': rec['price_range'],
                'image_url': rec['image_url'],
                'website': rec['resto_website'],
                'neighborhood': rec['neighborhood'].title(),
                'full_address': full_address
            })
            if 'resy_venue_url' in rec:
                if vision.res_mode_on:
                    restos_list[count]['resy_url'] = rec['resy_venue_url'].replace('<party_size>', f'{vision.party_size}').replace('<res_date>', f'{vision.res_date}') + f'&time={vision.res_time.replace(":", "")}'
                else:
                    restos_list[count]['resy_url'] = rec['resy_venue_url']
            # print(f"Final rec formatted for UI: \n{restos_list[count]}")
        
        # Insert input + recs into Mongo
        try:
            insert_result = mongo_recs.insert_one(insert_recs)
            print(f"Inserted recommendation to Mongo: {insert_result}")
        except pymongo.errors.OperationFailure:
            raise("Exception when inserting rec to Mongo. Are you sure your database user is authorized to perform write operations?")
        
        # Update User with input and recs in Mongo
        try:
            mongo_users = DB['users']
            rec_names = [rec['resto_name'] for rec in resto_recs]
            update_result = mongo_users.update_one(
                {"username": vision.username},
                {"$push": {
                    "inputs": vision.description,
                    "recs": {"$each": rec_names}
                }}
            )
            print(f"Updated User in Mongo: {update_result}")
        except pymongo.errors.OperationFailure:
            raise("Exception when inserting rec to Mongo. Are you sure your database user is authorized to perform write operations?")

        top_rec = restos_list[0]
        pitch = query_llm(restaurant_name=top_rec['resto_name'], review=top_rec['review'], vision=vision.description, openai_api_key=os.getenv('OPENAI_API_KEY'))
        # print(restos_list)
        if not used_reservations:
            print("Did NOT use reservation data for recs!", file=sys.stderr)
        else:
            print("DID use reservation data for recs!!", file=sys.stderr)
        return {
            'success': True,
            'restos': restos_list,
            'usedReservations': used_reservations,
            'usedBoth': used_neighborhood_and_cuisine,
            'usedNeighborhood': used_neighborhood,
            'usedCuisine': used_cuisine,
            'pitch': pitch
        }
    except Exception as e:
        return {
            'success': False,
            'error': "Congrats, you broke me! Jk, the dangerwiches were probably just a little too spicy... Arthur will fix me in a bit. Sorry for the interruption, I know you must be dying to get out and eat. Feel free to let Arthur know incase he's busy and doesn't notice this right away! In the meantime.. Broncos Country, Let's Ride." 
        }


