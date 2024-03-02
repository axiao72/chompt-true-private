# Helper functions
from src.resy_util import *
from src.mongo_util import *
from src.llm_util import *
from src.users import *
from src.constants import *
from src.google_util import *
import math
import pandas as pd
from copy import deepcopy


def get_recs(vision, post_metadata_filters, poi_string):
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
        df_cands = pd.DataFrame(candidates)
        # Get frequency of candidates
        df_cands['frequency'] = df_cands.groupby('restoName')['restoName'].transform('size')
        df_cands.sort_values(by='score', ascending=False, inplace=True)
        df_cands = df_cands.drop_duplicates(subset=['restoName', 'neighborhood'])
        print(f"Stage 1: Reduced to {len(df_cands)} unique candidates..")
        if post_metadata_filters:
            # For now, we use the top 3 filtered restaurants as our final recs,
            # will change to allow for scoring after filtering.
            df_cands = apply_filters(df_cands, post_metadata_filters)
            print(f"Filtered to {len(df_cands)} candidates.")
        df_cands = df_cands.round(6)
        cands_dict = df_cands.to_dict(orient='records')
        if vision.res_mode_on:
            backup_cands = deepcopy(cands_dict)
            print(f"Res Mode on: Filtering based on Resy availability...", file=sys.stderr)
            # Filter out restaurants not available for reservations
            cands_dict = get_top_available_candidates(cands_dict, vision.res_date, vision.res_time, vision.party_size)
            # If no available restaurants for reservations, use candidates without Resy filter
            if not cands_dict:
                print(f"Res Mode off. There were no available reservations among the candidates, proceeding without Res Mode....", file=sys.stderr)
                cands_dict = backup_cands
                used_reservations = False
        if poi_string:
            # If point of interest present in query, call gmaps distance function. TEST!!!
            cands_dict = get_geo_distances(cands_dict, poi_string)
        df_cands = pd.DataFrame(cands_dict)
        df_cands = score_recs(df_cands)
        df_cands = df_cands.round(6)
        final_cands = df_cands.to_dict(orient='records')
        final_recs = final_cands[0:3]
        # Print out similarity scores for each rec, just for my sake.
        for i in final_recs:
            print(
                f"\n{i['restoName']}:\nOriginal Similarity Search Score: {i['score']}\nAdjusted Score: {i['adjusted_score']}\nFrequncy: {i['frequency']}", 
                file=sys.stderr
            )
            if 'distance_to_origin' in i:
                print(f"Distance to poi: {i['distance_to_origin']}\n", file=sys.stderr)
        
        return final_recs, used_reservations
    
    except GoogleMapsError:
        raise
    except Exception as ex:
        print(f"Exception while getting recommendations: {ex}")
        raise


def apply_filters(df_candidates: pd.DataFrame, post_metadata_filters: dict):
    """
    Filter candidates further by (subject to change):
        - cuisine
        - neighborhood (if applicable from query)

    Args:
        candidates_df (pd.DataFrame): A pandas dataframe of candidate recommendations.
        post_metadata_filters (dict): A dictionary containing filters for post metadata.

    Returns:
        list: A pandas dataframe of candidates filtered by cuisine.

    This function filters the dataframe of candidates further based on the extracted filters.
    """
    print(f"Explicit Filter Stage: Filtering {len(df_candidates)} candidates further by cuisine and neighborhood...", file=sys.stderr)
    
    # print(candidates[0])
    print(f"Filtering with filters: {post_metadata_filters}", file=sys.stderr)
    try:
        # Loop through each candidate and add to filtered_cands if it fits the filters
        df_filtered = df_candidates.copy()
        for filt in post_metadata_filters:
            if filt == 'location':
                df_filt = 'neighborhood'
            else:
                df_filt = filt
            df_filtered = df_filtered[df_filtered[df_filt].isin(post_metadata_filters[filt])]
        if df_filtered.empty:
            return df_candidates
        else:
            return df_filtered
    except Exception as ex:
        raise ex


def score_recs_poi(candidates):
    """
    Apply point of interest scoring function to the candidates. 
    This scoring function takes into account:
        - Distance to the user's desired point of interest (extracted from their query).
        - Frequency of restaurant in similarity search results

    Args:
        candidates (list): A list of candidate recommendations.
    
    Returns:
        list: The candidates after applying scoring function, sorted by adjusted score.
    """
    scored_candidates = deepcopy(candidates)
    for cand in scored_candidates:
        distance_log = math.log(cand['distance_to_origin']) * 0.01
        cand['adjusted_score'] = cand['score'] - distance_log
    scored_candidates.sort(key=lambda x: x['adjusted_score'], reverse=True)
    return scored_candidates


def score_recs_neighborhood(candidates):
    """
    Apply non-point of interest scoring function to the candidates. 
    Distance is not used in this scoring because candidates should have been filtered by neighborhood.
    This scoring function takes into account:
        - Frequency of restaurant in similarity search results

    Args:
        candidates (list): A list of candidate recommendations.
    
    Returns:
        list: The candidates after applying scoring function, sorted by adjusted score.
    """
    scored_candidates = deepcopy(candidates)
    for cand in scored_candidates:
        distance_log = math.log(cand['distance_to_origin']) * 0.01
        cand['adjusted_score'] = cand['score'] - distance_log
    scored_candidates.sort(key=lambda x: x['adjusted_score'], reverse=True)
    return scored_candidates


def score_recs(df_candidates: pd.DataFrame):
    """
    Apply scoring function to the candidates. 
    This scoring function takes into account:
        - Frequency of restaurant in similarity search results
        - Distance to point of interest (only if user inputs poi)

    Args:
        df_candidates (pd.DataFrame): A dataframe of candidate recommendations.
    
    Returns:
        list: The candidates after applying scoring function, sorted by adjusted score.
    """
    scored_candidates = df_candidates.copy()
    # If distance to origin was calculated, then apply distance scoring
    if 'distance_to_origin' in scored_candidates:
        scored_candidates['distance_to_origin'] = scored_candidates['distance_to_origin'].astype(float)
        distance_scores = scored_candidates['distance_to_origin'].apply(lambda x: math.log(x) * 3 * 0.01)
    else:
        distance_scores = 0.0
    # Frequency scoring
    frequency_scores = 0.0
    # frequency_scores = scored_candidates['frequency'].apply(lambda x: x**5 * 0.0001)
    # Calculate adjusted scores separately
    adjusted_scores = scored_candidates['score'] + frequency_scores - distance_scores
    # Directly add adjusted scores to dataframe
    scored_candidates.loc[:, 'adjusted_score'] = adjusted_scores
    # Resort by adjusted score values
    scored_candidates.sort_values(by='adjusted_score', ascending=False, inplace=True)
    return scored_candidates


def isNaN(value):
    return value != value  # NaN is the only value that is not equal to itself


def replace_nan_with_none(d):
    return {k: None if isNaN(v) else v for k, v in d.items()}


def format_recs(resto_recs, vision):
    formatted_recs = []
    for rec in resto_recs:
        rec = replace_nan_with_none(rec)
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


def get_borough_neighborhoods(borough: str) -> list:
    # IMPLEMENT LIST OF NEIGHBORHOODS!!!
    borough_neighborhoods = {
        'manhattan': MANHATTAN,
        'brooklyn': BROOKLYN,
        'queens': QUEENS,
        'bronx': BRONX,
        'staten island': STATEN_ISLAND
    }
    neighborhoods = borough_neighborhoods.get(borough.lower(), None)
    return neighborhoods


