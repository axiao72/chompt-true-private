from fastapi import Body, FastAPI, Response
import uuid
from api.pydantic_models import *
from src.helpers import *


app = FastAPI()


@app.post("/api/signup")
async def signup(user: User, response: Response):
    try:
        new_user = await signup_user(user)
        # Generate uuid for session and add to session cookies
        generated_uuid = str(uuid.uuid4())
        print(f"Generated session uuid: {generated_uuid}", file=sys.stderr)
        response.set_cookie(key='session_uuid', value=generated_uuid)
        response.set_cookie(key='chompt_username', value=new_user['username'])
        session = await add_session(generated_uuid, new_user['username'])
        return {
            'username': new_user['username'],
            'firstName': new_user['firstName'],
            'lastName': new_user['lastName'],
            'inputs': new_user['inputs'],
            'resyClicks': new_user['resyClicks'],
            'success': True
        }
    except Exception as e:
        # Implement exception
        return {
            'success': False,
            'error': str(e)
        }


@app.post("/api/login")
async def login(credentials: LoginCredentials, response: Response):
    try:
        user = await login_user(credentials)
        # print(f"User from app_api: {user}")
        # Generate uuid for session and add to session cookies
        generated_uuid = str(uuid.uuid4())
        print(f"Generated session uuid: {generated_uuid}", file=sys.stderr)
        response.set_cookie(key='session_uuid', value=generated_uuid)
        response.set_cookie(key='chompt_username', value=user['username'])
        session = await add_session(generated_uuid, user['username'])
        return {
            'username': user['username'],
            'firstName': user['firstName'],
            'lastName': user['lastName'],
            'inputs': user['inputs'],
            'resyClicks': user['resyClicks'],
            'success': True
        }
    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }


# Clears session UUID from cookies
@app.post("/api/logout")
async def logout(response: Response):
    try:
        response.delete_cookie(key='session_uuid')  
        response.delete_cookie(key='chompt_username')
        return {
            'success': True,
            'message': 'Cleared cookies!'
        }
    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }


@app.post("/api/get_mongo_user_by_username/{username}")
async def get_mongo_user_by_username(username: str):
    try:
        user = await find_user_by_username(username)
        return {
            'username': user['username'],
            'firstName': user['firstName'],
            'lastName': user['lastName'],
            'inputs': user['inputs'],
            'resyClicks': user['resyClicks'],
            'success': True
        }
    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }
    

@app.post("/api/get_mongo_user_from_uuid/{uuid}")
async def get_mongo_user_by_uuid(uuid: str):
    try:
        user_session = await find_user_by_uuid(uuid)
        user = await find_user_by_username(user_session['username'])
        return {
            'username': user['username'],
            'firstName': user['firstName'],
            'lastName': user['lastName'],
            'inputs': user['inputs'],
            'resyClicks': user['resyClicks'],
            'success': True
        }
    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }
    

@app.post("/api/track_event")
async def track_activity(event: Event):
    try:
        mongo_client = connect_to_mongo()
        DB = mongo_client.chompt
        mongo_events = DB['events']
        event_data = dict(event)
        print(event_data, file=sys.stderr)
        mongo_events.insert_one(event_data)
        mongo_client.close()
        return {
            'success': True
        }
    except Exception as e:
        mongo_client.close()
        return {
            'success': False,
            'error': e
        }


@app.post("/api/chat")
async def chat(vision: IdealMeal):  
    try: 
        print(f"Getting recommendations in {vision.city} for the query: '{vision.description}'....", file=sys.stderr)
        # Extract cuisine and neighborhood for metadata filter. Keeping these as post filters just for extra layer of re-ranking/validation
        filters = extract_filters(vision.description)
        print(f"Got post search filters: {filters}")
        poi_string = '' # Will be used as a poi flag and for google distances api
        if filters['location']:
            location_str = ' '.join(filters['location'])
            location_type = classify_location(location_str)
            # If point of interest, set poi string and remove location from filters 
            # because we will be using it to score instead.
            print(f"Location Type: {location_type}", file=sys.stderr)
            if location_type == 'point of interest':
                poi_string = location_str
                del filters['location']
            # If borough, set location filter to list of all neighborhoods in the borough.
            elif location_type == 'borough':
                filters['location'] = get_borough_neighborhoods(location_str) # IMPLEMENT LIST OF NEIGHBORHOODS!!!
        # Get recommendations!
        resto_recs, used_reservations = get_recs(vision, filters, poi_string)
        print(f"Broncos Country... Let's Ride!!!", file=sys.stderr)
        # print(f"Got {len(resto_recs)} recs.", file=sys.stderr)
        # Format recs
        final_recs_list = format_recs(resto_recs, vision) 
        # print(f"Formatted recs: {final_recs_list}")
        # Insert input + recs into Mongo
        insert_result = insert_recs_mongo(vision, resto_recs)
        # Update User with input and recs in Mongo
        update_result = update_user_info(vision, resto_recs)
        # print(f"Final recs: {final_recs_list}")
        # Generate pitch for the top rec
        top_rec = final_recs_list[0]
        pitch = query_llm(restaurant_name=top_rec['resto_name'], review=top_rec['review'], vision=vision.description)
        
        if not used_reservations:
            print("Did NOT use reservation data for recs!", file=sys.stderr)
        else:
            print("DID use reservation data for recs!!", file=sys.stderr)
        final_recs_jsons = [json.dumps(d) for d in final_recs_list]
        return {
            'success': True,
            'restos': final_recs_jsons,
            'usedReservations': used_reservations,
            # 'usedBoth': used_neighborhood_and_cuisine,
            # 'usedNeighborhood': used_neighborhood,
            # 'usedCuisine': used_cuisine,
            'pitch': pitch
        }
    except GoogleMapsError as gmaps_ex:
        return {
            'success': False,
            'error': str(gmaps_ex)
        }
    except Exception as ex:
        return {
            'success': False,
            'error': "Congrats, you broke me! Jk, the dangerwiches were probably just a little too spicy... Arthur will fix me in a bit. Sorry for the interruption, I know you must be dying to get out and eat. Feel free to let Arthur know incase he's busy and doesn't notice this right away! In the meantime.. Broncos Country, Let's Ride." 
        }


