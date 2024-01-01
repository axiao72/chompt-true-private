from bs4 import BeautifulSoup
from urllib.request import urlopen
import json
import requests
# import re
# import time
import pickle
from typing import List
import pinecone
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.chat_models import ChatOpenAI
from langchain.llms import OpenAI
from langchain.chains.llm import LLMChain
from langchain.vectorstores import Pinecone
from langchain.text_splitter import CharacterTextSplitter, RecursiveCharacterTextSplitter
from langchain.schema.document import Document
from langchain.prompts import PromptTemplate
from langchain.output_parsers import PydanticOutputParser
from langchain.pydantic_v1 import BaseModel as LangchainBaseModel, Field, validator
from datetime import datetime
import os
import random
import sys
from tqdm.auto import tqdm
from uuid import uuid4
import sys
from src.prompts import *
import time
from api.pydantic_models import IdealMeal


class Restaurant(LangchainBaseModel):
    # Pydantic class for extracting entities using LLM
    cuisine: List[str] = Field(description="List of cuisines of a restaurant")
    neighborhood: List[str] = Field(description="List of neighborhoods a restaurant is located in")


def initialize_pinecone(api_key, environment):
    # Initialize Pinecone
    pinecone.init(
        api_key=api_key,
        environment=environment,
    )


def store_reviews(filename: str, embed_model: HuggingFaceEmbeddings, index_name):
    try:
        # If pinecone index already exists, delete and create new. 
        # Only using this function if want to create a new, updated index
        if index_name in pinecone.list_indexes():
            pinecone.delete_index(index_name)
            pinecone.create_index(
                    name=index_name,
                    metric='cosine',
                    dimension=1024 # 1024 dim of e5-large-v2
            )
        # Get Pinecone index
        index = pinecone.Index(index_name)
        # Get reviews from file
        with open(filename, 'rb') as file:
            resto_reviews = pickle.load(file)

        text_splitter = RecursiveCharacterTextSplitter(chunk_size=2500,
                                        chunk_overlap=800,
                                        length_function=len)
        
        # Chunk limit for upserting to Pinecone
        batch_limit = 30
        batch_count = 1

        upsert_chunks = []
        upsert_metadatas = []

        total_word_cnt = 0

        start_time = datetime.now()
        print(f"Start time: {start_time}", file=sys.stderr)
        # Split and prepare each review
        for i, resto in enumerate(tqdm(resto_reviews)):
            print(f"Chunking and preparing review #{i}...", file=sys.stderr)
            # Clean up review data
            cleaned_review = resto['review'].replace('&apos;', "'").replace("&amp;", "&").replace('&quot;', '"').replace("&quot", '"')
            cleaned_resto_name = resto['resto_name'].replace("&amp;", "&").replace('&apos;', "'")
            cleaned_resto_tags = resto['perfect_for_tags'].replace("&amp;", "&").replace('&apos;', "'")
            review_date = resto['review_date'].split('T')[0]
            
            # Set the metadata for this restaurant review
            metadata = {
                'resto_name': cleaned_resto_name,
                'cuisine': resto['cuisine'],
                'perfect_for_tags': cleaned_resto_tags,
                'price_range': resto['price_range'],
                'review_date': review_date,
                'image_url': resto['resto_image'],
            }
            # Split review into chunks
            review_chunks = text_splitter.split_text(cleaned_review)
            # Add the perfect-for tags and cuisine to the beginning of each review chunk so this becomes part of the embedding
            review_chunks = [f"Perfect for: {cleaned_resto_tags}. Serves {resto['cuisine']}. " + j for j in review_chunks]
            # Create metadata dicts for each chunk
            chunk_metadatas = [{
                "chunk": j, "text": text, **metadata
            } for j, text in enumerate(review_chunks)]
            # Append chunks to list of chunks (to be upserted to Pinecone)
            upsert_chunks.extend(review_chunks)
            # Append chunks metadatas to list of metadatas (also to be upserted to Pinecone)
            upsert_metadatas.extend(chunk_metadatas)
            # If we're at the batch_limit, store chunks in Pinecone
            if len(upsert_chunks) >= batch_limit:
                # Generate uuids for each chunk
                ids = [str(uuid4()) for _ in range(len(upsert_chunks))]
                # embed the chunks
                embeddings = embed_model.embed_documents(upsert_chunks)
                print(f"Batch full. Upserting dangerwich batch #{batch_count}...", file=sys.stderr)
                # Upsert the chunks
                index.upsert(vectors=zip(ids, embeddings, upsert_metadatas))
                print(f"Finished upserting dangerwich batch #{batch_count}!!!", file=sys.stderr)
                # Clear the batch of chunks and metadatas for the next batch
                upsert_chunks = []
                upsert_metadatas = []

        # If there are any left over chunks, upsert them
        if upsert_chunks:
            print("Upserting left over dangerwiches...", file=sys.stderr)
            ids = [str(uuid4()) for _ in range(len(upsert_chunks))]
            embeddings = embed_model.embed_documents(upsert_chunks)
            index.upsert(vectors=zip(ids, embeddings, upsert_metadatas))
        print("Finished upserting all dangerwiches... Broncos Country. Let's Ride.", file=sys.stderr)
        end_time = datetime.now()
        print(f"End time: {end_time}", file=sys.stderr)
        print(f"Total elapsed time: {end_time - start_time}", file=sys.stderr)
    except Exception as e:
        print(f"Exception occured while storing infatuation reviews in Pinecone: {e}", file=sys.stderr)


def extract_entities(query: str, openai_api_key):
    # Extract cuisine and/or neighborhood to use as metadata filters
    llm = OpenAI(
    openai_api_key=openai_api_key,
    temperature=0, 
    model="text-davinci-003"
    )

    parser = PydanticOutputParser(pydantic_object=Restaurant)
    pydantic_prompt = PromptTemplate(
        template=PYDANTIC_TEMPLATE,
        input_variables=['query'],
        partial_variables={"format_instructions": parser.get_format_instructions()},
    )

    extract_input = pydantic_prompt.format_prompt(query=query)
    # print(f"Using prompt: {extract_input.to_string()}", file=sys.stderr)
    try:
        output = llm(extract_input.to_string())
        filters = parser.parse(output)
        # metadata_filter = {} # Pinecone filter
        metadata_filter = {'$and':[]} # Mongo filter
        if filters.cuisine:
            # Mongo filter
            metadata_filter['$and'].append(
                {
                    'cuisine': {"$in": [i.lower() for i in filters.cuisine]}
                }
            )
            # metadata_filter['cuisine'] = {"$in": [filters.cuisine.lower()]} # Pinecone filter
        if filters.neighborhood:
            # Mongo filter
            metadata_filter['$and'].append(
                {
                    'neighborhood': {"$in": [i.lower() for i in filters.neighborhood]}
                }
            )
            # metadata_filter['neighborhood'] = {"$in": [filters.neighborhood.lower()]} # Pinecone filter
    except Exception as e:
        print(f"Exception while extracting cuisine and neighborhood: {e}", file=sys.stderr)
        metadata_filter = {'$and':[]} # Keep empty if exception happens so recommendation can continue without filters
    return metadata_filter


def get_top_restos_mongo(vision: IdealMeal, embed_model: HuggingFaceEmbeddings, mongo_reviews, metadata_filters):
    res_mode_on = vision.res_mode_on
    query = vision.description
    embedded_query = embed_model.embed_query(query)
    try:
        # Keep track if reservation filter was used in final recommendations so we can display to user
        used_reservations = res_mode_on
        # Restos are returned containing appropriate metadata and reviews
        # Prepare mongo vector search pipeline
        pipeline = [
            {
                '$vectorSearch': {
                    'index': 'reviews_content_index',
                    'path': 'content_embedding',
                    'queryVector': embedded_query,
                    'numCandidates': 45,
                    'limit': 3
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
        if metadata_filters['$and']:
            print(f"Searching vector database with metadata filters: {metadata_filters}..." , file=sys.stderr)
            pipeline[0]['$vectorSearch']['filter'] = metadata_filters
            # If Res Mode is on, change limit to same as candidates to perform candidate generation then the first 3 that have available reservations
            if res_mode_on:
                pipeline[0]['$vectorSearch']['limit'] = 45  # same as numCandidates (assign separately to avoid accidentally changing numCandidates later or something)
                print(f"Res Mode is ON. Generating candidates...")
                candidates = list(mongo_reviews.aggregate(pipeline))
                print(f"Generated Candidates. Getting final recs based on Resy availability...")
                top_restos = get_top_available_candidates(candidates, vision.res_date, vision.res_time, vision.party_size)
                pipeline[0]['$vectorSearch']['limit'] = 3  # set back to 3 for downstream recs if needed
            # If Res Mode is off, continue without separate candidate generation step
            else:
                top_restos = list(mongo_reviews.aggregate(pipeline))
            # If Res Mode is on and no results with reservations filter, run again without reservation filters but keep other filters
            if len(top_restos) == 0 and res_mode_on:
                print(f"Search with available restaurants returned no results. Re-running vector database search without reservation availability, but with other metadata filters..." , file=sys.stderr)
                # Delete the last filter expression, assuming the last one is the available reservations filter.
                del pipeline[0]['$vectorSearch']['filter']['$and'][-1]
                print(f"Removed available res filter")
                top_restos = list(mongo_reviews.aggregate(pipeline))
                used_reservations = False
            # If no results from basic metadata filter, remove all filters and run again
            if len(top_restos) == 0:
                print(f"Metadata filter search returned no results. Re-running vector database search with no metadata filters at all..." , file=sys.stderr)
                removed_filter = pipeline[0]['$vectorSearch'].pop('filter')
                print(f"Removed filter: {removed_filter}")
                top_restos = list(mongo_reviews.aggregate(pipeline))
        else:
            print(f"Searching vector database with no metadata filters..." , file=sys.stderr)
            top_restos = list(mongo_reviews.aggregate(pipeline))
        print(f"Found the top {len(top_restos)} recommendations!! Watch out... their spppiiiicccyyyyyyy...", file=sys.stderr)
        for i in top_restos:
            print(f"{i['resto_name']} similarity search score: {i['score']}\n")
    except Exception as e:
        print(f"Exception occured while vector searching Mongo: {e}") 
        top_restos = []   
    return top_restos, used_reservations


def get_top_restos_pinecone(query: str, embed_model: HuggingFaceEmbeddings, index, metadata_filters):
    embedded_query = embed_model.embed_query(query)
    # vector_store = Pinecone.from_existing_index(index_name, embed_model)
    # Restos are returned containing appropriate metadata and reviews
    if metadata_filters:
        print(f"Searching vector database with metadata filters: {metadata_filters}..." , file=sys.stderr)
        top_restos = index.query(
            vector=embedded_query,
            filter=metadata_filters,
            top_k=3,
            include_metadata=True
        )['matches']
        if len(top_restos) == 0:
            print(f"Metadata filter search returned no results. Re-running vector database search with no metadata filters..." , file=sys.stderr)
            top_restos = index.query(vector=embedded_query, top_k=3, include_metadata=True)['matches']
    else:
        print(f"Searching vector database with no metadata filters..." , file=sys.stderr)
        top_restos = index.query(vector=embedded_query, top_k=3, include_metadata=True)['matches']
    # Get actual resto data from matches key
    print("Found the top 3 restaurants!! Watch out... their spppiiiicccyyyyyyy...", file=sys.stderr)
    for i in top_restos:
        print(f"{i.metadata['resto_name']} similarity search score: {i.score}\n")
    return top_restos


def query_llm(restaurant_name: str, review: str, vision: str, openai_api_key):
    llm = ChatOpenAI(
        openai_api_key=openai_api_key,
        model_name='gpt-3.5-turbo',
        temperature=0.0
    )
    convince_prompt = PromptTemplate(
        template=CONVINCE_PROMPT_TEMPLATE,
        input_variables=['restaurant_name', 'review', 'vision']
    )
    convince_chain = LLMChain(llm=llm, prompt=convince_prompt)
    response = convince_chain(
        {
            "restaurant_name": restaurant_name,
            "review": review,
            "vision": vision,
        },
        return_only_outputs=True
    )
    return response.get('text')


def instantiate_embed_model(model_name: str, model_type: str):
    if model_type == 'OpenAI':
        embed_model = OpenAIEmbeddings(
                    document_model_name=model_name,
                    query_model_name=model_name,
                    openai_api_key=os.getenv('OPENAI_API_KEY')
                )
    elif model_type.lower() == 'hf':
        # Initialize e5-large-v2 embeddings model
        model_kwargs = {'device': 'cpu'}
        encode_kwargs = {'normalize_embeddings': False}

        embed_model = HuggingFaceEmbeddings(model_name=model_name,
                                            model_kwargs=model_kwargs,
                                            encode_kwargs=encode_kwargs)
    return embed_model


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
    final_candidates = []
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
    while i < len(candidates) and len(final_candidates) < 3:
        print(f"Checking candidate #{i+1} availability")
        cand = candidates[i]
        data['query'] = cand['resy_venue_name']
        response = requests.post(
            url,
            data=json.dumps(data),
            headers=headers
        )
        if response.status_code == 200:
            resy_json = json.loads(response.text)
            if (len(resy_json['search']['hits'][0]['availability']['slots'])) > 0:
                final_candidates.append(cand)
                print(f"Found available candidate! Candidate #{i+1}")
        else:
            print(f"Error: {response.status_code}")
        i += 1
    print(f"Returning {len(final_candidates)} final candidates.")
    return final_candidates
