import pymongo
from tqdm.auto import tqdm

# Connect to Mongo
try:
    client = pymongo.MongoClient("mongodb+srv://axiao72:McSplash7013$@chomptcluster.k5sqjpd.mongodb.net/?retryWrites=true&w=majority")
    print("Connected to Mongo!")
except pymongo.errors.ConfigurationError:
    print("Invalid URI host, confirm Atlas host name and password is correct in the connection string!")

# Connect to Chompt db and reviews collection
db = client.chompt 
# mongo_reviews = db["reviews"]
mongo_reviews_w_resy = db["chunked_reviews_openai"]
mongo_reviews_wo_resy = db["chunked_reviews_openai_150_30"]
# mongo_reviews_wo_resy = db["reviews"]

# Get all reviews with resy data
resy_reviews_list = list(mongo_reviews_w_resy.find({'hasResy': True}))
visited_reviews = []

for resto in tqdm(resy_reviews_list):
    resto_name = resto['restoName']
    resto_neighborhood = resto['neighborhood']
    resto_city = resto['city']
    resto_combo = f"{resto_name} {resto_neighborhood} {resto_city}"
    # Check if already processed this review's resy data
    if resto_combo in visited_reviews:
        continue
    visited_reviews.append(resto_combo)
    mongo_reviews_wo_resy.update_many(
        {"restoName": resto_name, "neighborhood": resto_neighborhood, "city": resto_city},
        {"$set": {
            "resy_venue_id": resto['resy_venue_id'], 
            "resy_venue_name": resto['resy_venue_name'], 
            "resy_venue_url": resto['resy_venue_url'],
            "hasResy": True
        }}
    )

    
