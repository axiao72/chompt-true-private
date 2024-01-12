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
mongo_reviews = db["reviews"]
# mongo_chunked_reviews = db["chunked_reviews"]
# CAREFUL only delete if you want to restart a collection fresh
# deleted = mongo_chunked_reviews.delete_many({})
# print(f"Deleted {deleted.deleted_count} records.")

# Read infatuation reviews from file for each city and insert them to Mongo
cities = ['new-york', 'pittsburgh', 'philadelphia', 'denver', 'washington-dc', 'los-angeles', 'boston', 'chicago']
start_time = datetime.now()
print(f"Insertion start time: {start_time}")
for city in cities:
    with open(f'../docker_webscraping/infatuation_reviews_v6_{city}.json', 'r') as file:
        resto_reviews = json.load(file)
    print(f"Read {len(resto_reviews)}  reviews from file for {city}. Inserting into reviews collection now...")

    batch_limit = 30
    batch_count = 1

    insert_datas = []

    total_word_cnt = 0

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
            cleaned_city = city.replace("-", " ")

            # # Check if the restaurant is already in Mongo. If it is, skip. (Unless adding updated reviews)
            # check_mongo = list(mongo_reviews.find({"$and": [{"resto_name": cleaned_resto_name}, {"neighborhood": neighborhood}, {"review_date": review_date}]}))
            # if check_mongo:
            #     print(f"Mongo already has a review for {cleaned_resto_name} from {review_date}! Skipping...")
            #     continue
            
            # Set the data for this restaurant review
            review_data = {
                'resto_name': cleaned_resto_name,
                'cuisine': cuisine,
                'perfect_for_tags': cleaned_resto_tags,
                'price_range': resto['price_range'],
                'review_date': review_date,
                'image_url': resto['resto_image'],
                'resto_website': resto['resto_website'],
                'neighborhood': neighborhood,
                'city': cleaned_city,
                'hasResy': False,
                'text': cleaned_review
            }
            
            insert_datas.append(review_data)
            # If we're at the batch_limit, store chunks in Pinecone
            if len(insert_datas) >= batch_limit:
                # ids = [unidecode(f"infatuation_{i['resto_name'].replace(' ', '_')}") for i in upsert_metadatas]
                # Embed each review chunk
                print(f"Batch full. Inserting reviews for dangerwich batch #{batch_count}...")
                # Insert the review data to Mongo
                insert_result = mongo_reviews.insert_many(insert_datas)
                print(f"Finished inserting dangerwich batch #{batch_count}!!!")
                batch_count += 1
                insert_datas = []
        except Exception as e:
            print(f"Exception while storing {cleaned_resto_name}: {e}")

    if len(insert_datas) > 0:
        print("Inserting left over dangerwiches...")
        # ids = [str(uuid4()) for _ in range(len(upsert_chunks))]
        insert_result = mongo_reviews.insert_many(insert_datas)
    print(f"Finished inserting all dangerwiches for city {city}... BRONCOS COUNTRY. LET'S RIDE!!!")

end_time = datetime.now()
print(f"End time: {end_time}")
print(f"Total elapsed time: {end_time - start_time}")