import pymongo
import sys


try:
    client = pymongo.MongoClient("mongodb+srv://axiao72:McSplash7013$@chomptcluster.k5sqjpd.mongodb.net/?retryWrites=true&w=majority")
except pymongo.errors.ConfigurationError:
    print("Invalid URI host, confirm Atlas host name and password i socrrect in the connection string!")

# Create CHOMPT database
db = client.chompt 

# # Create Reviews collection
reviews = db["reviews"]
try:
    result = reviews.insert_one({"name": "test"})
    print("Created and inserted into reviews collection!")
    print(f"Inserted 1 review!")
except pymongo.errors.OperationFailure:
    print("An authentication error was received. Are you sure your database user is authorized to perform write operations?")

# # Create Recommendations collection
recommendations = db["recommendations"]
try:
    result = recommendations.insert_one({"name": "test"})
    print("Created and inserted into recommendations collection!")
    print(f"Inserted 1 recommendation!")
except pymongo.errors.OperationFailure:
    print("An authentication error was received. Are you sure your database user is authorized to perform write operations?")

# Create Users collection
users = db["users"]
users.drop() 
user_documents = [
    {
        "first_name": "Arthur",
        "last_name": "Xiao",
        "dob": "2/11/1999",
        "cuisine_prefs": ["chinese", "mexican", "mediterranean", "italian", "middle eastern"],
        "neighborhood": "east village",
        "has_been_to": []
    },
    {
        "first_name": "Aedan",
        "last_name": "Collins",
        "dob": "1/31/1999",
        "cuisine_prefs": ["italian", "mexican", "american", "mediterranean"],
        "neighborhood": "williamsburg",
        "has_been_to": []
    },
    {
        "first_name": "Margot",
        "last_name": "Shea",
        "dob": "4/20/1999",
        "cuisine_prefs": ["mediterranean", "chinese", "thai", "italian", "mexican"],
        "neighborhood": "east village",
        "has_been_to": []
    }
]
try:
    result = users.insert_many(user_documents)
    print("Created and inserted into users collection!")
    print(f"Inserted {len(result.inserted_ids)} users!")
except pymongo.errors.OperationFailure:
    print("An authentication error was received. Are you sure your database user is authorized to perform write operations?")


# # Create Restaurants collection
restaurants = db["restaurants"]
try:
    result = restaurants.insert_one({"name": "test"})
    print("Created and inserted into restaurants collection!")
    print(f"Inserted 1 restaurant!")
except pymongo.errors.OperationFailure:
    print("An authentication error was received. Are you sure your database user is authorized to perform write operations?")

# # Create Ratings collection
ratings = db["ratings"]
try:
    result = ratings.insert_one({"name": "test"})
    print("Created and inserted into ratings collection!")
    print(f"Inserted 1 rating!")
except pymongo.errors.OperationFailure:
    print("An authentication error was received. Are you sure your database user is authorized to perform write operations?")
