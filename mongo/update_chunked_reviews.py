import pickle
import pymongo
from langchain.text_splitter import CharacterTextSplitter, RecursiveCharacterTextSplitter
from langchain.schema.document import Document
import more_itertools
from datetime import datetime
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.vectorstores import Pinecone
import os
from dotenv import load_dotenv
from tqdm.auto import tqdm
import json
from unidecode import unidecode


# Connect to Mongo
try:
    client = pymongo.MongoClient("mongodb+srv://axiao72:McSplash7013$@chomptcluster.k5sqjpd.mongodb.net/?retryWrites=true&w=majority")
    print("Connected to Mongo!")
except pymongo.errors.ConfigurationError:
    print("Invalid URI host, confirm Atlas host name and password i socrrect in the connection string!")

# Connect to Chompt db and reviews collection
db = client.chompt 
mongo_chunked_reviews = db["chunked_reviews"]
# mongo_chunked_reviews = db["chunked_reviews"]
# CAREFUL only delete if you want to restart a collection fresh
# deleted = mongo_chunked_reviews.delete_many({})
# print(f"Deleted {deleted.deleted_count} records.")

# Read infatuation reviews from file for each city and insert them to Mongo
# cities = ['pittsburgh', 'philadelphia', 'denver', 'washington-dc', 'los-angeles', 'boston', 'chicago']
cities = ['new-york']
start_time = datetime.now()
print(f"Embeddings start time: {start_time}")
for city in cities:
    # with open(f'../docker_webscraping/infatuation_reviews_v6_{city}.json', 'r') as file:
    with open(f'../docker_webscraping/infatuation_reviews_v6.json', 'r') as file:
        resto_reviews = json.load(file)
    print(f"Read {len(resto_reviews)}  reviews from file for {city}. Updating city now...")

    updated = []

    for i, resto in enumerate(tqdm(resto_reviews)):
        try:
            # print(f"Chunking and preparing review #{i}...")
            # Clean up review data
            cleaned_review = resto['review'].replace('&apos;', "'").replace("&amp;", "&").replace('&quot;', '"').replace("&quot", '"')
            cleaned_resto_name = resto['resto_name'].replace("&amp;", "&").replace('&apos;', "'").replace('&quot;', '"').replace("&quot", '"').lower()
            cleaned_resto_tags = resto['perfect_for_tags'].replace("&amp;", "&").replace('&apos;', "'").lower()
            review_date = resto['review_date'].split('T')[0]
            neighborhood = resto['resto_neighborhood'].split('/')[-1].replace('-', ' ').lower()
            cuisine = resto['cuisine'].lower()
            # cleaned_city = resto['city'].replace("-", " ")
            cleaned_city = city.replace("-", " ")

            # Loop through review docs for this restaurant location and update with summary 
            cursor = mongo_chunked_reviews.find({
                'resto_name': cleaned_resto_name,
                'cuisine': cuisine,
                'perfect_for_tags': cleaned_resto_tags,
                'price_range': resto['price_range'],
                'review_date': review_date,
                'image_url': resto['resto_image'],
                'resto_website': resto['resto_website'],
                'neighborhood': neighborhood
            })
            for doc in cursor:
                mongo_chunked_reviews.update_one({'_id': doc['_id']}, 
                                        {"$set": {'city': cleaned_city}})
            
        except Exception as e:
            print(f"Exception while updating {cleaned_resto_name}: {e}")

end_time = datetime.now()
print(f"End time: {end_time}")
print(f"Total elapsed time: {end_time - start_time}")