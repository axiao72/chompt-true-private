# Helper functions
from src.resy_util import *
from src.mongo_util import *
from src.llm_util import *
from src.users import *
from src.constants import *


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
            if candidate['resto_name'] not in unique_cand_names:
                unique_cands.append(candidate)
                unique_cand_names.append(candidate['resto_name'])
        print(f"Stage 1: Reduced to {len(unique_cands)} unique candidates..")
        if vision.res_mode_on:
            print(f"Res Mode on: Filtering based on Resy availability...", file=sys.stderr)
            # Filter out restaurants not available for reservations
            unique_cands = get_top_available_candidates(unique_cands, vision.res_date, vision.res_time, vision.party_size)
            # If no available restaurants for reservations, re-generate candidates without Resy filter
            if not unique_cands:
                print(f"Res Mode on: Filtering based on Resy availability...", file=sys.stderr)
                unique_cand_names = []
                unique_cands = []
                candidates = get_candidates(embedded_query, vision.city, False)
                for candidate in candidates:
                    if candidate['resto_name'] not in unique_cand_names:
                        unique_cands.append(candidate)
                        unique_cand_names.append(candidate['resto_name'])
                used_reservations = False
        if post_metadata_filters:
            # For now, we use the top 3 filtered restaurants as our final recs,
            # will change to allow for scoring after filtering.
            final_recs = apply_filters(unique_cands, post_metadata_filters)
        else:
            final_recs = unique_cands[0:3]
            print(f"No filters provided. Got top {len(final_recs)} recs.", file=sys.stderr)
        # Print out similarity scores for each rec, just for my sake.
        for i in final_recs:
            print(f"{i['resto_name']} similarity search score: {i['score']}\n", file=sys.stderr)
        
        return final_recs, used_reservations
    
    except Exception as ex:
        raise(f"Exception occured while getting recommendations: {ex}")


def apply_filters(candidates, post_metadata_filters):
    filtered_cands = []
    print(f"Final Stage: Filtering further by cuisine and neighborhood if possible...", file=sys.stderr)
    filter_cnt = 0  # To keep track of which filter i'm using
    # Loop through each available candidate applying appropriate filters to get final recs (can be less than 3)
    while not filtered_cands and filter_cnt < 4:
        i = 0
        while i < len(candidates) and len(filtered_cands) < 3 and filter_cnt < 3:
            cand = candidates[i]
            # Filter on both neighborhood and cuisine for final 3 recs
            if filter_cnt == 0:
                if ('cuisine' in post_metadata_filters and 'neighborhood' in post_metadata_filters) and (cand['cuisine'] in post_metadata_filters['cuisine'] and cand['neighborhood'] in post_metadata_filters['neighborhood']):
                    filtered_cands.append(cand)
                    print("Used both Neighborhood and Cuisine filters!", file=sys.stderr)
            # Filter on neighborhood for final 3 recs if no recs with both neighborhood AND cuisine (prioritize neighborhood)
            elif filter_cnt == 1:
                if 'neighborhood' in post_metadata_filters and cand['neighborhood'] in post_metadata_filters['neighborhood']:
                    filtered_cands.append(cand)
                    print("Used just Neighborhood filter!", file=sys.stderr)
            # Filter on cuisine for final 3 recs if no recs with just neighborhood
            elif filter_cnt == 2:
                if 'cuisine' in post_metadata_filters and cand['cuisine'] in post_metadata_filters['cuisine']:
                    filtered_cands.append(cand)
                    print("Used just Cuisine filter!", file=sys.stderr)
            i += 1
        filter_cnt += 1
        # If filter_cnt == 3, we exhausted all filters. Just take top 3 available restos
        if filter_cnt == 3:
            filtered_cands = candidates[0:3]
            print("Used just reservation availability.", file=sys.stderr)

    return filtered_cands


async def format_recs(resto_recs, vision):
    formatted_recs = []
    for count, rec in enumerate(resto_recs):
        full_review_doc = await get_full_review(rec)
        if 'summarized_review' in full_review_doc:
            full_review = full_review_doc['summarized_review']
        else:
            full_review = full_review_doc['text']
        if 'geo' in full_review_doc:
            full_address = full_review_doc['geo']['fullAddress']
        else:
            full_address = ''
        # Format Resy URL
        if 'resy_venue_url' in rec:
            if vision.res_mode_on:
                resy_url = rec['resy_venue_url'].replace('<party_size>', f'{vision.party_size}').replace('<res_date>', f'{vision.res_date}') + f'&time={vision.res_time.replace(":", "")}'
            else:
                resy_url = rec['resy_venue_url']
        else:
            resy_url = ''
        # Add desired fields to final list
        formatted_recs.append({
            'resto_name': capitalize_resto_name(rec['resto_name']),
            'review': full_review,
            'perfect_for': rec['perfect_for_tags'],
            'price_range': rec['price_range'],
            'image_url': rec['image_url'],
            'website': rec['resto_website'],
            'neighborhood': rec['neighborhood'].title(),
            'full_address': full_address,
            'resy_url': resy_url
        })
    return formatted_recs


def capitalize_resto_name(string):
    result = []
    words = string.split()
    for word in words:
        result.append(word.capitalize())
    return " ".join(result)