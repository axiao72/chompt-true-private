import sys
from datetime import datetime
from api.pydantic_models import IdealMeal
from src.resy_util import *
from src.constants import *


def get_search_pipeline(embedded_query):
    pipeline = [
        {
            '$vectorSearch': {
                'index': EMBEDDINGS_INDEX,
                'path': 'content_embedding',
                'queryVector': embedded_query,
                'numCandidates': NUM_CANDIDATES,
                'limit': NUM_CANDIDATES
            }
        }, {
            '$project': {
                '_id': 0,
                'text': 1,
                'reviewDate': 1,
                'restoName': 1,
                'cuisine': 1,
                'perfectForTags': 1,
                'priceRange': 1,
                'priceRange': 1,
                'imageUrl': 1,
                'restoWebsite': 1,
                'neighborhood': 1,
                'resy_venue_id': 1,
                'resy_venue_name': 1,
                'resy_venue_url': 1,
                'city': 1,
                'geo': 1,
                'score': {
                    '$meta': 'vectorSearchScore'
                }
            }
        }
    ]
    return pipeline


def get_candidates(embedded_query, city, res_mode_on: bool):
    try:
        print(f"Stage 1: Searching vector database for candidates..." , file=sys.stderr)
        db = MONGO_CLIENT.chompt
        mongo_reviews = db[EMBEDDINGS_COLLECTION_NAME]

        pipeline = get_search_pipeline(embedded_query)
        if res_mode_on:
            # add city and {'hasResy': True} to vector search filter and remove hasResy from filters
            pipeline[0]['$vectorSearch']['filter'] = {'$and': [{'city': city}, {'hasResy': res_mode_on}]}
        else:
            pipeline[0]['$vectorSearch']['filter'] = {'city': city}
        candidates = list(mongo_reviews.aggregate(pipeline))

        return candidates
    except Exception as ex:
        raise(f"Exception occured while vector searching Mongo: {ex}") 


async def add_session(uuid: str, username: str):
    try:
        db = MONGO_CLIENT.chompt
        mongo_sessions = db['sessions']
        session = {
            'uuid': uuid,
            'username': username
        }
        insert_result = mongo_sessions.insert_one(session)
        print(f'Created new session for {username}', file=sys.stderr)
        return insert_result
    except Exception as e:
        raise(e)


def insert_recs_mongo(vision, recs):
    """Insert the batch of recommendations into Mongo (watch out, they're spiiiicy!)"""
    try:
        # print(f"From insert_recs_mongo: {recs}")
        # Connect to Mongo
        db = MONGO_CLIENT.chompt
        mongo_recs = db["recommendations"]
        
        insert_recs = {
            'username': vision.username,
            'date': datetime.today().strftime('%Y-%m-%d'),
            'user_input': vision.description,
            'reservation_mode': vision.res_mode_on
        }
        for count, rec in enumerate(recs):
            insert_recs[f'restaurant{count+1}_name'] = rec['restoName']
            insert_recs[f'restaurant{count+1}_score'] = rec['score']
        # Insert input + recs into Mongo
        try:
            insert_result = mongo_recs.insert_one(insert_recs)
            # print(f"Inserted recommendation to Mongo: {insert_result}")
            return insert_result
        except pymongo.errors.OperationFailure:
            raise("Exception when inserting rec to Mongo. Are you sure your database user is authorized to perform write operations?")
    except Exception as ex:
        raise(f'Exception while inserting recs into Mongo: {ex}')
    

def get_full_review(rec):
    # Connect to Mongo
    db = MONGO_CLIENT.chompt
    full_reviews = db['reviews']
    try:
        full_review = full_reviews.find_one({
            'resto_name': rec['restoName'].lower(), 
            'neighborhood': rec['neighborhood'],
            'city': rec['city']
        })
        return full_review
    except pymongo.errors.OperationFailure:
        raise("Exception when getting full review from Mongo. Are you sure your database user is authorized to perform write operations?")
