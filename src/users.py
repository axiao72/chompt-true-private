import pymongo
import sys
from api.pydantic_models import *
from src.mongo_util import *
from passlib.hash import bcrypt


async def signup_user(user: User):
    print(f"Recieved username: {user.username}", file=sys.stderr)
    print(f"Recieved password: {user.password}", file=sys.stderr)
    print(f"Recieved first name: {user.first_name}", file=sys.stderr)
    print(f"Recieved last name: {user.last_name}", file=sys.stderr)

    # Validate sign up fields
    if not user.username or not user.password or not user.first_name or not user.last_name:
        raise Exception("Must fill out all fields.")

    DB = connect_to_mongo()
    mongo_users = DB['users']

    # Check if Mongo already has user
    user_exists = list(mongo_users.find({'username': user.username}))
    print(f"Mongo search result: {user_exists}", file=sys.stderr)
    if user_exists:
        raise Exception("Username already exists!")
    else: 
        print(f"User not already in Mongo, adding now!", file=sys.stderr)
    
    pw_to_hash = user.password
    # Hash password
    hashed_pw = bcrypt.hash(pw_to_hash)
    print(f"Hashed password!", file=sys.stderr)

    # Store new user with username and password in Mongo
    new_user = {
        'username': user.username, 
        'password': hashed_pw, 
        'firstName': user.first_name,
        'lastName': user.last_name,
        'inputs': 0,
        'resyClicks': 0
    }
    try:
        result = mongo_users.insert_one(new_user)
        # Return inserted user with hashed password if Mongo insert worked
        print(f"Inserted user: {new_user}", file=sys.stderr)
        return new_user
    except pymongo.errors.OperationFailure:
        raise Exception("Exception occured during insert of new user to Mongo!")


async def login_user(credentials: LoginCredentials):
    print(credentials.username, file=sys.stderr)
    # Validate login fields
    if not credentials.username or not credentials.password:
        raise Exception("Must provide username and password.")
    
    DB = connect_to_mongo()
    mongo_users = DB['users']

    # Get user by username
    user = mongo_users.find_one({'username': credentials.username})
    if not user:
        raise Exception("Username not found.")
    else:
        print(f"User {credentials.username} found!", file=sys.stderr)
    # Check if inputted password matches user's stored password
    match = bcrypt.verify(credentials.password, user['password'])
    if match:
        # Passwords match! Return User Mongo Doc.
        print("Correct password! Returning logged in user.", file=sys.stderr)
        return user
    else:
        print("Not a match!", file=sys.stderr)
        raise Exception("Incorrect password")
    

async def find_user_by_username(username: str):
    DB = connect_to_mongo()
    mongo_users = DB['users']
    user = mongo_users.find_one({'username': username})
    if not user:
        print(f"Error in find_user_by_username", file=sys.stderr)
        raise Exception("Username not found.")
    else:
        print(f"User {username} found!", file=sys.stderr)
        return user
    

async def find_user_by_uuid(uuid: str):
    DB = connect_to_mongo()
    mongo_sessions = DB['sessions']
    user_session = mongo_sessions.find_one({'uuid': uuid})
    if not user_session:
        print(f"Error in find_user_by_uuid", file=sys.stderr)
        raise Exception(f"User session not found with UUID: {uuid}.")
    else:
        print(f"Session for {user_session['username']} found!", file=sys.stderr)
        return user_session
        
