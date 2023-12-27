import pymongo
from langchain.text_splitter import CharacterTextSplitter, RecursiveCharacterTextSplitter
from datetime import datetime
from langchain.embeddings import HuggingFaceEmbeddings
from tqdm.auto import tqdm
import json


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

# Connect to Chompt db and resy collection
db = client.chompt 
mongo_resy = db["resy"]

# CAREFUL only delete if you want to restart a collection fresh
# deleted = mongo_resy.delete_many({})
# print(f"Deleted {deleted.deleted_count} records.")

# Read resy venues from file and insert them to Mongo
with open('../resy/all_resy_venues_v2.json', 'r') as file:
    resy_venues = json.load(file)
print("Read resy venues from file.")

batch_limit = 30
batch_count = 1

insert_datas = []

start_time = datetime.now()
print(f"Embeddings start time: {start_time}")
for i, venue in tqdm(enumerate(resy_venues)):
    try:
        print(f"Preparing venue #{i}")
        # If Mongo already has this venue, skip it
        already_contains = list(mongo_resy.find({'venue_id': venue['resy_venue_id']}))
        if already_contains:
            print(f"Mongo already has this venue! Moving on...")
            continue
        # Format metadata
        venue_metadata = {
            'venue_name': venue['resy_venue_name'],
            'venue_id': venue['resy_venue_id'],
            'venue_url': venue['resy_venue_url'],
            'venue_neighborhood': venue['resy_venue_neighborhood']
        }
        # Add to metadata list to be inserted to Mongo
        insert_datas.append(venue_metadata)
        # Once metadata list is at batch limit, insert the list to Mongo as a batch
        if len(insert_datas) >= batch_limit:
            print(f"Batch full. Embedding venue names for batch #{batch_count}")
            # Venue names to embed
            venue_names = [data['venue_name'] for data in insert_datas]
            # Embed venue names
            embeddings = embeddings_model.embed_documents(venue_names)
            # Combo venue name and neighborhood (if neighborhood is already in name, just use name. else, combo)
            name_and_neighborhoods = [data['venue_name'] if data['venue_neighborhood'] in data['venue_name'] else f"{data['venue_name']} {data['venue_neighborhood']}" for data in insert_datas]
            # Embed combo name and neighborhood
            combo_embeddings = embeddings_model.embed_documents(name_and_neighborhoods)
            # Loop through the venue data and add embeddings field
            for count, data in enumerate(insert_datas):
                data['venue_name_embedding'] = embeddings[count]
                data['venue_combo_embedding'] = combo_embeddings[count]
            print(f"Inserting resy venues batch #{batch_count}...")
            # Insert the venue data to Mongo
            insert_result = mongo_resy.insert_many(insert_datas)
            print(f"Finished inserting resy venues batch #{batch_count}!!!")
            batch_count += 1
            insert_datas = []
    except Exception as e:
        print(f"Exception while processing batch #{batch_count}")
if len(insert_datas) > 0:
    print("Inserting left over resy venues...")
    venue_names = [data['venue_name'] for data in insert_datas]
    embeddings = embeddings_model.embed_documents(venue_names)
    # Loop through the venue data and add embeddings field
    for count, data in enumerate(insert_datas):
        data['venue_name_embedding'] = embeddings[count]
    insert_result = mongo_resy.insert_many(insert_datas)
print("Finished inserting all resy venues... BRONCOS COUNTRY. LET'S RIDE!!!")

end_time = datetime.now()
print(f"End time: {end_time}")
print(f"Total elapsed time: {end_time - start_time}")