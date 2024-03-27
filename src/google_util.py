from src.constants import GMAPS_CLIENT
from src.exceptions import GoogleMapsError
from copy import deepcopy
import sys


def feet_to_miles(feet: float) -> float:
    miles = feet / 5280
    return miles


def get_geo_distances(restos: list, query_origin: str):
    """
    Calculates the distance of each restaurant candidate from the user's specified origin using Google's Maps API.

    Parameters:
    - restos (list): A dict of restaurants with all the fields from Mongo.
    - query_origin (str): Location extracted from the user's input query, aka where they are looking for a restaurant.

    Returns:
    list: List of resto dictionaries with each resto's distance (in miles) from the query origin appended to its dictionary entry.
    """
    try:
        distance_restos = deepcopy(restos)
        origins = [query_origin]
        destinations = [{"lat": resto['geo']['latitude'], "lng": resto['geo']['longitude']} for resto in restos]
        destination_batches = [destinations[i:i+25] for i in range(0, len(destinations), 25)]

        final_distances = []
        # IMPLEMENT ERROR HANDLING FOR WHEN GMAPS CAN'T FIND THE POI
        for dest_batch in destination_batches:
            result_distances = GMAPS_CLIENT.distance_matrix(
                origins, 
                dest_batch, 
                mode="walking",
                units='imperial'
            )
            final_distances.extend(result_distances['rows'][0]['elements'])
        for idx, resto in enumerate(distance_restos):
            if 'distance' not in final_distances[idx]:
                return restos
            # Currently using miles, could use just meters from value field to make it more direct,
            # but would have to adjust scoring
            distance_str = final_distances[idx]['distance']['text']
            if 'ft' in distance_str:
                distance_mi = feet_to_miles(float(distance_str.split()[0]))
            else:
                distance_mi = float(distance_str.split()[0])
            resto['distanceToOrigin'] = distance_mi

        return distance_restos
    except:
        print(f"Exception while getting distances from Google Maps for {query_origin}")
        raise GoogleMapsError("Could not find your point of interest on Google Maps! Try again with the full name of the point of interest, or use another one.")