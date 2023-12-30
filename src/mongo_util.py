from langchain.embeddings import HuggingFaceEmbeddings
import pymongo
import sys
from api.pydantic_models import IdealMeal
from src.resy_util import *


def connect_to_mongo():
    # Connect to Mongo chompt database and return database object
    try:
        MONGO_CLIENT = pymongo.MongoClient("mongodb+srv://axiao72:McSplash7013$@chomptcluster.k5sqjpd.mongodb.net/?retryWrites=true&w=majority")
        DB = MONGO_CLIENT.chompt
        print("Connected to Mongo!")
        return DB
    except pymongo.errors.ConfigurationError:
        print("Invalid URI host, confirm Atlas host name and password is correct in the connection string!")
        return None


# Post-filter searches
def get_recs_mongo_non_res_mode(vision: IdealMeal, embed_model: HuggingFaceEmbeddings, mongo_reviews, collection_name, post_metadata_filters):
    query = vision.description
    embedded_query = embed_model.embed_query(query)
    final_recs = []
    final_recs_names = []
    # Keep track of which filters were used in final recommendations so we can display to user
    used_neighborhood_and_cuisine = False
    used_neighborhood = False
    used_cuisine = False
    if collection_name == 'reviews':
        index = 'reviews_content_index'
    elif collection_name == 'chunked_reviews':
        index= 'chunked_reviews_content_index'
    try:
        # Prepare mongo vector search pipeline
        pipeline = get_search_pipeline(index, embedded_query=embedded_query, num_candidates=45, limit=45)
        print(f"Stage 1: Searching vector database for candidates with just User's query..." , file=sys.stderr)
        candidates = list(mongo_reviews.aggregate(pipeline))
        print(f"Stage 1: Generated {len(candidates)} candidates..")
        print(f"Final Stage: Filtering further by cuisine and neighborhood if possible...")
        # If filters were extracted, apply them in prioritized order
        if post_metadata_filters:
            filter_cnt = 0  # To keep track of which filter i'm using
            # Loop through each available candidate applying appropriate filters to get final recs (can be less than 3)
            while not final_recs and filter_cnt < 4:
                i = 0
                while i < len(candidates) and len(final_recs) < 3 and filter_cnt < 3:
                    cand = candidates[i]
                    # Filter on both neighborhood and cuisine for final 3 recs
                    if filter_cnt == 0:
                        if ('cuisine' in post_metadata_filters and 'neighborhood' in post_metadata_filters) and (cand['cuisine'] in post_metadata_filters['cuisine'] and cand['neighborhood'] in post_metadata_filters['neighborhood']) and cand['resto_name'] not in final_recs_names:
                            final_recs.append(cand)
                            final_recs_names.append(cand['resto_name'])
                            used_neighborhood_and_cuisine = True
                            print("Used both Neighborhood and Cuisine filters!")
                    # Filter on neighborhood for final 3 recs if no recs with both neighborhood AND cuisine (prioritize neighborhood)
                    elif filter_cnt == 1:
                        if 'neighborhood' in post_metadata_filters and cand['neighborhood'] in post_metadata_filters['neighborhood'] and cand['resto_name'] not in final_recs_names:
                            final_recs.append(cand)
                            used_neighborhood = True
                            print("Used just Neighborhood filter!")
                    # Filter on cuisine for final 3 recs if no recs with just neighborhood
                    elif filter_cnt == 2:
                        if 'cuisine' in post_metadata_filters and cand['cuisine'] in post_metadata_filters['cuisine'] and cand['resto_name'] not in final_recs_names:
                            final_recs.append(cand)
                            used_cuisine = True
                            print("Used just Cuisine filter!")
                    i += 1
                filter_cnt += 1
                # If filter_cnt == 3, we exhausted all filters. Just take top 3 available restos
                if filter_cnt == 3:
                    j = 0
                    while j < len(candidates) and len(final_recs) < 3:
                        cand = candidates[j]
                        if cand['resto_name'] not in final_recs_names:
                            final_recs.append(cand)
                            final_recs_names.append(cand['resto_name'])
                    print("Used just query.")
        # If no filters, just get top 3 candidates
        else:
            j = 0
            while j < len(candidates) and len(final_recs) < 3:
                cand = candidates[j]
                if cand['resto_name'] not in final_recs_names:
                    final_recs.append(cand)
                    final_recs_names.append(cand['resto_name'])
                j += 1
            print(f'No filters provided. Got top {len(final_recs)} recs.')
        for i in final_recs:
            print(f"{i['resto_name']} similarity search score: {i['score']}\n")
    except Exception as e:
        print(f"Exception occured while vector searching Mongo: {e}") 
        final_recs = [] 
    return final_recs, used_neighborhood_and_cuisine, used_neighborhood, used_cuisine


# Post-filter searches
# When Reservation Mode is on, reservation availability is top priority!!! If user turned it on, this means they don't want to deal with walk-ins!
def get_recs_mongo_res_mode(vision: IdealMeal, embed_model: HuggingFaceEmbeddings, mongo_reviews, collection_name, post_metadata_filters):
    res_mode_on = vision.res_mode_on
    query = vision.description
    embedded_query = embed_model.embed_query(query)
    final_recs = []
    final_recs_names = []
    # Keep track of which filters were used in final recommendations so we can display to user
    used_reservations = res_mode_on
    used_neighborhood_and_cuisine = False
    used_neighborhood = False
    used_cuisine = False
    if collection_name == 'reviews':
        index = 'reviews_content_index'
    elif collection_name == 'chunked_reviews':
        index= 'chunked_reviews_content_index'
    try:
        # Restos are returned containing appropriate metadata and reviews
        # Get mongo vector search pipeline
        pipeline = get_search_pipeline(index, embedded_query=embedded_query, num_candidates=45, limit=45)
        # Initial Candidate generation
        print(f"Stage 1: Searching vector database for reservation data candidates..." , file=sys.stderr)
        # add {'hasResy': True} to vector search filter and remove from filters
        pipeline[0]['$vectorSearch']['filter'] = {'hasResy': post_metadata_filters.pop('hasResy')}
        candidates = list(mongo_reviews.aggregate(pipeline))
        print(f"Stage 1: Generated {len(candidates)} candidates..")
        print(f"Stage 2: Filtering based on Resy availability...", file=sys.stderr)
        available_candidates = get_top_available_candidates(candidates, vision.res_date, vision.res_time, vision.party_size)
        # If there are any available candidates, do final filtering stage
        if available_candidates:
            # If filters were extracted, apply them in prioritized order
            if post_metadata_filters:
                print(f"Final Stage: Filtering further by cuisine and neighborhood if possible...", file=sys.stderr)
                filter_cnt = 0  # To keep track of which filter i'm using
                # Loop through each available candidate applying appropriate filters to get final recs (can be less than 3)
                while not final_recs and filter_cnt < 4:
                    i = 0
                    while i < len(available_candidates) and len(final_recs) < 3 and filter_cnt < 3:
                        cand = available_candidates[i]
                        # Filter on both neighborhood and cuisine for final 3 recs
                        if filter_cnt == 0:
                            if ('cuisine' in post_metadata_filters and 'neighborhood' in post_metadata_filters) and (cand['cuisine'] in post_metadata_filters['cuisine'] and cand['neighborhood'] in post_metadata_filters['neighborhood']) and cand['resto_name'] not in final_recs_names:
                                final_recs.append(cand)
                                used_neighborhood_and_cuisine = True
                                print("Used both Neighborhood and Cuisine filters!", file=sys.stderr)
                        # Filter on neighborhood for final 3 recs if no recs with both neighborhood AND cuisine (prioritize neighborhood)
                        elif filter_cnt == 1:
                            if 'neighborhood' in post_metadata_filters and cand['neighborhood'] in post_metadata_filters['neighborhood'] and cand['resto_name'] not in final_recs_names:
                                final_recs.append(cand)
                                used_neighborhood = True
                                print("Used just Neighborhood filter!", file=sys.stderr)
                        # Filter on cuisine for final 3 recs if no recs with just neighborhood
                        elif filter_cnt == 2:
                            if 'cuisine' in post_metadata_filters and cand['cuisine'] in post_metadata_filters['cuisine'] and cand['resto_name'] not in final_recs_names:
                                final_recs.append(cand)
                                used_cuisine = True
                                print("Used just Cuisine filter!", file=sys.stderr)
                        i += 1
                    filter_cnt += 1
                    # If filter_cnt == 3, we exhausted all filters. Just take top 3 available restos
                    if filter_cnt == 3:
                        final_recs = available_candidates[0:3]
                        print("Used just reservation availability.", file=sys.stderr)
            # If no filters, just get top 3 candidates
            else:
                j = 0
                while j < len(available_candidates) and len(final_recs) < 3:
                    cand = available_candidates[j]
                    if cand['resto_name'] not in final_recs_names:
                        final_recs.append(cand)
                        final_recs_names.append(cand['resto_name'])
                    j += 1
                print(f"No filters provided. Got top {len(final_recs)} recs.", file=sys.stderr)
        # If no available candidates on Resy, then do non-reservation mode search as last resort
        else:
            final_recs, used_neighborhood_and_cuisine, used_neighborhood, used_cuisine = get_recs_mongo_non_res_mode(vision, embed_model, mongo_reviews, post_metadata_filters)
            used_reservations = False
            print("Did not use reservation mode.")
        for i in final_recs:
            print(f"{i['resto_name']} similarity search score: {i['score']}\n", file=sys.stderr)
    except Exception as e:
        print(f"Exception occured while vector searching Mongo: {e}", file=sys.stderr) 
        final_recs = [] 
    return final_recs, used_reservations, used_neighborhood_and_cuisine, used_neighborhood, used_cuisine  


def get_search_pipeline(index: str, embedded_query, num_candidates: int, limit: int):
    pipeline = [
        {
            '$vectorSearch': {
                'index': index,
                'path': 'content_embedding',
                'queryVector': embedded_query,
                'numCandidates': num_candidates,
                'limit': limit
            }
        }, {
            '$project': {
                '_id': 0,
                'text': 1,
                'resto_name': 1,
                'cuisine': 1,
                'perfect_for_tags': 1,
                'price_range': 1,
                'image_url': 1,
                'resto_website': 1,
                'neighborhood': 1,
                'resy_venue_id': 1,
                'resy_venue_name': 1,
                'resy_venue_url': 1,
                'score': {
                    '$meta': 'vectorSearchScore'
                }
            }
        }
    ]
    return pipeline
