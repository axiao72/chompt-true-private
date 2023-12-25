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


# Initialize e5-large-v2 embeddings model
print("Instantiating embeddings model...")
model_kwargs = {'device': 'cpu'}
encode_kwargs = {'normalize_embeddings': False}

embeddings_model = HuggingFaceEmbeddings(model_name="intfloat/e5-large-v2",
                                     model_kwargs=model_kwargs,
                                     encode_kwargs=encode_kwargs)
print("Instantiated embeddings model!")

# Connect to Mongo
try:
    client = pymongo.MongoClient("mongodb+srv://axiao72:McSplash7013$@chomptcluster.k5sqjpd.mongodb.net/?retryWrites=true&w=majority")
    print("Connected to Mongo!")
except pymongo.errors.ConfigurationError:
    print("Invalid URI host, confirm Atlas host name and password i socrrect in the connection string!")

# Connect to Chompt db and reviews collection
db = client.chompt 
mongo_reviews = db["reviews"]
# CAREFUL only delete if you want to restart a collection fresh
# deleted = mongo_reviews.delete_many({})
# print(f"Deleted {deleted.deleted_count} records.")

# Read infatuation reviews from file and insert them to Mongo
with open('../docker_webscraping/infatuation_reviews_v5.json', 'r') as file:
    resto_reviews = json.load(file)
print("Read reviews from file.")

text_splitter = RecursiveCharacterTextSplitter(chunk_size=3500,
                                 chunk_overlap=1000,
                                 length_function=len)

batch_limit = 30
batch_count = 1

insert_chunks = []
insert_datas = []

total_word_cnt = 0

start_time = datetime.now()
print(f"Embeddings start time: {start_time}")
for i, resto in enumerate(tqdm(resto_reviews)):
    try:
        print(f"Chunking and preparing review #{i}...")
        # Clean up review data
        cleaned_review = resto['review'].replace('&apos;', "'").replace("&amp;", "&").replace('&quot;', '"').replace("&quot", '"')
        cleaned_resto_name = resto['resto_name'].replace("&amp;", "&").replace('&apos;', "'")
        cleaned_resto_tags = resto['perfect_for_tags'].replace("&amp;", "&").replace('&apos;', "'")
        review_date = resto['review_date'].split('T')[0]
        neighborhood = resto['resto_neighborhood'].split('/')[-1].replace('-', ' ').lower()

        # Check if the restaurant is already in Mongo. If it is, skip. (Unless adding updated reviews)
        check_mongo = mongo_reviews.find_one({"$and": [{"resto_name": cleaned_resto_name}, {"review_date": review_date}]})
        if check_mongo is not None:
            print(f"Mongo already has a review for {cleaned_resto_name} from {review_date}! Skipping...")
            continue
        
        # Set the metadata for this restaurant review
        review_data = {
            'resto_name': cleaned_resto_name,
            'cuisine': resto['cuisine'].lower(),
            'perfect_for_tags': cleaned_resto_tags,
            'price_range': resto['price_range'],
            'review_date': review_date,
            'image_url': resto['resto_image'],
            'resto_website': resto['resto_website'],
            'neighborhood': neighborhood
        }
        # Split review into chunks
        review_chunks = text_splitter.split_text(cleaned_review)
        # Make copy of original chunk texts to go into metadata 
        # (so we don't add additional data to the metadata 'text' field in the next step)
        original_chunks = review_chunks
        # Add other text to review chunk that we want to be included in the embedding
        review_chunks = [f"Perfect for: {cleaned_resto_tags}. Serves {resto['cuisine']}. Located in the {neighborhood} neighborhood. " + j for j in review_chunks]
        print(f"Word count of review chunk: {len(review_chunks[0])}")
        # Create metadata dicts for each chunk
        chunk_datas = [{
            "chunk": j, "text": text, **review_data
        } for j, text in enumerate(original_chunks)]
        # Append chunks to list of chunks (to be inserted to Mongo)
        insert_chunks.extend(review_chunks)
        # Append chunks datas to list of datas (also to be inserted to Mongo)
        insert_datas.extend(chunk_datas)
        # If we're at the batch_limit, store chunks in Pinecone
        if len(insert_chunks) >= batch_limit:
            # ids = [unidecode(f"infatuation_{i['resto_name'].replace(' ', '_')}") for i in upsert_metadatas]
            # Embed each review chunk
            print(f"Batch full. Embedding chunks for batch {batch_count}...")
            embeddings = embeddings_model.embed_documents(insert_chunks)
            # Loop through the review data entries and add the embedding field
            for h, data in enumerate(insert_datas):
                data['content_embedding'] = embeddings[h]
            print(f"Inserting dangerwich batch #{batch_count}...")
            # Insert the review data to Mongo
            insert_result = mongo_reviews.insert_many(insert_datas)
            print(f"Finished inserting dangerwich batch #{batch_count}!!!")
            batch_count += 1
            insert_chunks = []
            insert_datas = []
    except Exception as e:
        print(f"Exception while storing {cleaned_resto_name}: {e}")

if len(insert_datas) > 0:
    print("Inserting left over dangerwiches...")
    # ids = [str(uuid4()) for _ in range(len(upsert_chunks))]
    embeddings = embeddings_model.embed_documents(insert_chunks)
    for h, data in enumerate(insert_datas):
        data['content_embedding'] = embeddings[h]
    insert_result = mongo_reviews.insert_many(insert_datas)
print("Finished inserting all dangerwiches... BRONCOS COUNTRY. LET'S RIDE!!!")

end_time = datetime.now()
print(f"End time: {end_time}")
print(f"Total elapsed time: {end_time - start_time}")