import pymongo
from urllib.request import urlopen
import json
import requests
import re
from datetime import datetime
from tqdm.auto import tqdm
import random
import time
from langchain.embeddings import HuggingFaceEmbeddings


# Initialize e5-large-v2 embeddings model
model_kwargs = {'device': 'cpu'}
encode_kwargs = {'normalize_embeddings': False}

embeddings_model = HuggingFaceEmbeddings(model_name="intfloat/e5-large-v2",
                                     model_kwargs=model_kwargs,
                                     encode_kwargs=encode_kwargs)

# Connect to Mongo
try:
    client = pymongo.MongoClient("mongodb+srv://axiao72:McSplash7013$@chomptcluster.k5sqjpd.mongodb.net/?retryWrites=true&w=majority")
    print("Connected to Mongo!")
except pymongo.errors.ConfigurationError:
    print("Invalid URI host, confirm Atlas host name and password i socrrect in the connection string!")

# Connect to Chompt db, and reviews and resy collection
db = client.chompt 
mongo_reviews = db["reviews"]
mongo_resy = db["resy"]

current_date = datetime.today().strftime('%Y-%m-%d')
# date needs to be in "YYYY-MM-DD" format
res_date = current_date
party_size = 2
resy_counter = 0

# Get all Mongo documents
mongo_docs = list(mongo_reviews.find())
print(f"Got {len(mongo_docs)} documents from Mongo. Cheffing up Resy data with similarity search now...")
start_time = datetime.now()
print(f"Embeddings start time: {start_time}")
for doc in tqdm(mongo_docs):
    name = doc['resto_name']
    cleaned_name = name.replace('&quot;', '"').replace("&quot", '"')
    neighborhood = doc['neighborhood']
    print(f"Getting Resy info for {name}... Truss...")
    # Check if Mongo has multiple documents with the restaurant name. If it does, add neighborhood to the query.
    docs_w_name = list(mongo_reviews.find({"resto_name": name}))
    if len(docs_w_name) > 1:
        print(f"{name} has multiple Infatuation Mongo docs. Sim Searching with name and neighborhood combined...")
        search_query = f"{cleaned_name} {neighborhood}"
    else:
        print(f"{name} has 1 Infatuation Mongo doc. Sim Searching with just name...")
        search_query = cleaned_name
    embedded_query = embeddings_model.embed_query(search_query)
    pipeline = [
            {
                '$vectorSearch': {
                    'index': 'resy_venue_name_index',
                    'path': 'venue_name_embedding',
                    'queryVector': embedded_query,
                    'numCandidates': 45,
                    'limit': 3
                }
            }, {
                '$project': {
                    '_id': 0,
                    'venue_name': 1,
                    'venue_id': 1,
                    'venue_url': 1,
                    'score': {
                        '$meta': 'vectorSearchScore'
                    }
                }
            }
        ]
    venue_matches = list(mongo_resy.aggregate(pipeline))
    top_match = venue_matches[0]
    score_threshold = 0.92
    if top_match['score'] >= 0.92:
        print(f"Similarity search found Resy restaurant and hit {score_threshold} threshold.")
        mongo_reviews.update_many(
                    {"resto_name": name, "neighborhood": neighborhood},
                    {"$set": {
                        f"resy_venue_id": top_match['venue_id'], 
                        f"resy_venue_name": top_match['venue_name'], 
                        f"resy_venue_url": top_match['venue_url']
                    }}
                )
        resy_counter += 1
        print(f"Updated {name} in Mongo with Resy info! Cheffed up Resy info for {resy_counter} Infatuation restos so far.")
    else:
        print(f"No Resy restaurants hit the {score_threshold} similarity threshold for {name} ._.")

end_time = datetime.now()
print(f"End time: {end_time}")
print(f"Total elapsed time: {end_time - start_time}")
