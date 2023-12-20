from fastapi import Body, FastAPI
from pydantic import BaseModel
from typing import Optional
from typing import Annotated
import pymongo
# from dotenv import load_dotenv

from src.py_ai_util import *


class IdealMeal(BaseModel):
    description: str


app = FastAPI()

# load_dotenv()
EMBED_MODEL = instantiate_embed_model("intfloat/e5-large-v2", 'HF')

# Initialize Pinecone vector db
# initialize_pinecone(api_key=os.getenv('PINECONE_API_KEY'), environment=os.getenv('PINECONE_ENVIRONMENT'))
# Store restaurant reviews in Pinecone
# store_reviews(filename='data/reviews.pkl', embed_model=EMBED_MODEL, index_name=os.getenv('PINECONE_INDEX_NAME'))

# Initialize Pinecone index
# INDEX = pinecone.Index(os.getenv('PINECONE_INDEX_NAME'))

# Connect to Mongo
try:
    MONGO_CLIENT = pymongo.MongoClient("mongodb+srv://axiao72:McSplash7013$@chomptcluster.k5sqjpd.mongodb.net/?retryWrites=true&w=majority")
    DB = MONGO_CLIENT.chompt
    print("Connected to Mongo!")
except pymongo.errors.ConfigurationError:
    print("Invalid URI host, confirm Atlas host name and password is correct in the connection string!")


@app.post("/api/chat")
async def chat(vision: IdealMeal):    
    mongo_reviews = DB["reviews"]
    # vision_dict = vision.model_dump()
    print(f"Getting recommendations for the query: '{vision.description}'....", file=sys.stderr)
    # Extract cuisine and neighborhood for metadata filter
    metadata_filters = extract_entities(vision.description, os.getenv('OPENAI_API_KEY'))
    # Get recommendations
    resto_recs = get_top_restos_mongo(
        query=vision.description, 
        embed_model=EMBED_MODEL, 
        mongo_reviews=mongo_reviews,
        metadata_filters=metadata_filters
    )
    print(f"Broncos Country... Let's Ride!!!", file=sys.stderr)
    # Insert recommended restaurants into Mongo
    mongo_recs = DB["recommendations"]
    insert_recs = {
        'user_input': vision.description
    }
    # (Don't need to do this with Mongo) Get just the review and metadata, without the sim search score
    # resto_recs_wo_score = [i['metadata'] for i in resto_recs]
    restos_list = []        
    for count, rec in enumerate(resto_recs):
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
    
    try:
        insert_result = mongo_recs.insert_one(insert_recs)
        print(f"Inserted recommendation to Mongo: {insert_result}")
    except pymongo.errors.OperationFailure:
        print("An authentication error was received. Are you sure your database user is authorized to perform write operations?")
    
    top_rec = restos_list[0]
    pitch = query_llm(restaurant_name=top_rec['resto_name'], review=top_rec['review'], vision=vision.description, openai_api_key=os.getenv('OPENAI_API_KEY'))
    
    return {
        'restos': restos_list,
        'pitch': pitch
    }