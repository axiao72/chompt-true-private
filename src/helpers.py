# Helper functions
from src.resy_util import *
from src.mongo_util import *
from src.llm_util import *
from src.users import *
from src.constants import *
from src.google_util import *


def get_recs(vision, post_metadata_filters):
    try:
        # Embed query
        query = vision.description
        embedded_query = EMBED_MODEL.embed_query(query)
        final_recs = []

        # Keep track of which filters were used in final recommendations so we can display to user
        used_reservations = vision.res_mode_on
        used_cuisine = False
        unique_cand_names = []
        unique_cands = []
        candidates = get_candidates(embedded_query, vision.city, vision.res_mode_on)
        print(f"Stage 1: Generated {len(candidates)} candidates..")
        # Get unique candidates. Going to change later to boost according to frequency
        for candidate in candidates:
            if candidate['restoName'] not in unique_cand_names:
                unique_cands.append(candidate)
                unique_cand_names.append(candidate['restoName'])
        print(f"Stage 1: Reduced to {len(unique_cands)} unique candidates..")
        if post_metadata_filters:
            backup_unique_cands = unique_cands.copy()
            # For now, we use the top 3 filtered restaurants as our final recs,
            # will change to allow for scoring after filtering.
            unique_cands = apply_filters(unique_cands, post_metadata_filters)
            print(f"Filtered to {len(unique_cands)} candidates.")
            if not unique_cands:
                unique_cands = backup_unique_cands
        if vision.res_mode_on:
            print(f"Res Mode on: Filtering based on Resy availability...", file=sys.stderr)
            backup_unique_cands = unique_cands.copy()
            # Filter out restaurants not available for reservations
            unique_cands = get_top_available_candidates(unique_cands, vision.res_date, vision.res_time, vision.party_size)
            # If no available restaurants for reservations, re-generate candidates without Resy filter
            if not unique_cands:
                print(f"Res Mode off. There were no available reservations among the candidates, proceeding without Res Mode....", file=sys.stderr)
                unique_cands = backup_unique_cands
                used_reservations = False
        final_recs = unique_cands[0:3]
        # Print out similarity scores for each rec, just for my sake.
        for i in final_recs:
            print(f"{i['restoName']} similarity search score: {i['score']}\n", file=sys.stderr)
        
        return final_recs, used_reservations
    
    except Exception as ex:
        raise(f"Exception occured while getting recommendations: {ex}")


def apply_filters(candidates, post_metadata_filters):
    """
    Filter candidates further by (subject to change):
        - cuisine
        - neighborhood

    Args:
        candidates (list): A list of candidate recommendations.
        post_metadata_filters (dict): A dictionary containing filters for post metadata.

    Returns:
        list: A list of candidates filtered by cuisine.

    This function filters the list of candidates further by cuisine based on the specified filters.
    It removes candidates whose cuisine does not match any of the cuisines specified in the post metadata filters.
    """
    print(f"Explicit Filter Stage: Filtering {len(candidates)} candidates further by cuisine and neighborhood...", file=sys.stderr)
    # print(candidates[0])
    filtered_cands = []
    filter_match = True
    try:
        # Loop through each candidate and add to filtered_cands if it fits the filters
        for cand in candidates:
            if all(cand[filter] in post_metadata_filters[filter] for filter in post_metadata_filters):
                filtered_cands.append(cand)
        return filtered_cands
    except Exception as ex:
        raise ex


def score_recs(candidates, query_origin):
    """
    Apply scoring function to the remaining candidates. 
    As of now, the scoring function takes into account:
        - distance to the user's desired location (extracted from their query).

    Args:
        candidates (list): A list of candidate recommendations.
    
    Returns:
        list: The top 3 candidates after applying our scoring function.

    Once the scores for each candidate have been adjusted according to the scoring function,
    the top 3 highest scored candidates will be returned.
    """
    candidates = get_geo_distances(candidates, query_origin, get_gmaps_client())


def format_recs(resto_recs, vision):
    formatted_recs = []
    for rec in resto_recs:
        full_review_doc = get_full_review(rec)
        # print(f"full review: {full_review_doc}")
        # print(f"{full_review_doc['resto_name']}: {full_review_doc.keys()}")
        if 'summarized_review' in full_review_doc:
            full_review = full_review_doc['summarized_review']
        else:
            full_review = full_review_doc['text']
        if 'geo' in full_review_doc:
            full_address = full_review_doc['geo']['fullAddress']
        else:
            full_address = ''
        # Format Resy URL
        resy_url = ''
        # print(f'REC: {rec}')
        if 'resy_venue_url' in rec:
            if vision.res_mode_on:
                resy_url = rec['resy_venue_url'].replace('<party_size>', f'{vision.party_size}').replace('<res_date>', f'{vision.res_date}') + f'&time={vision.res_time.replace(":", "")}'
            else:
                resy_url = rec['resy_venue_url']

        # Add desired fields to final list
        formatted_recs.append({
            'resto_name': capitalize_resto_name(rec['restoName']),
            'review': full_review,
            'perfect_for': rec['perfectForTags'],
            'price_range': rec['priceFange'],
            'image_url': rec['imageUrl'],
            'website': rec['restoWebsite'],
            'neighborhood': rec['neighborhood'].title(),
            'full_address': full_address,
            'resy_url': resy_url
        })
    print('FORMATTED recs!')
    return formatted_recs


def capitalize_resto_name(string):
    result = []
    words = string.split()
    for word in words:
        result.append(word.capitalize())
    return " ".join(result)