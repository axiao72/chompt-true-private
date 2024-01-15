from bs4 import BeautifulSoup
from urllib.request import urlopen
import json
import requests
import re
import time
import pickle
from tqdm.auto import tqdm
from lxml import html
import random

cities = ['new-york', 'pittsburgh', 'philadelphia', 'denver', 'washington-dc', 'los-angeles', 'boston', 'chicago']
for city in cities:
    print(f"Getting reviews for {city}!")
    
    with open(f'already_scraped_urls_{city}.txt', 'r') as file:
        review_urls = file.read().splitlines()

    # with open('already_scraped_urls.pkl', 'rb') as file:
    #     already_scraped_urls = pickle.load(file)

    resto_reviews = []

    url_prefix = "https://www.theinfatuation.com"
    for count, url in enumerate(tqdm(review_urls)):
        try:
            review_page = urlopen(f"https://www.theinfatuation.com{url}")
            html = review_page.read().decode("utf-8")
            soup = BeautifulSoup(html, 'lxml')
            
            # Get website URL and neighborhood from list of links within the review
            website_url = ''
            neighborhood = ''
            for link in soup.html.select('a'):
                if "Website" in link:
                    website_url = link['href']
                elif "neighborhoods" in link['href']:
                    neighborhood = link['href']

            # Get review dictionary from Soup
            review_dict = json.loads(soup.script.string)
            
            # Get resto name
            resto_name = review_dict['itemReviewed']['name']
            
            # Entire review body split into list containing normal review and food rundown section
            review_body = review_dict['reviewBody']
            review_split = review_body.split('Food Rundown')
            
            # Just review
            just_review = review_split[0]
            
            # Food Rundown
            if len(review_split) > 1:
                food_rundown = review_split[1]
            else:
                food_rundown = ''

            # Review price
            review_price = review_dict['itemReviewed']['priceRange']
            
            # Key words
            review_tags = review_dict['itemReviewed']['keywords']
            
            # Cuisine
            review_cuisine = review_dict['itemReviewed']['servesCuisine']
            
            # Date of Review
            review_date = review_dict['dateModified']
            
            # Image of Restaurant 
            try:
                resto_image_url = review_dict['itemReviewed']['image']
            except Exception as e:
                resto_image_url = ''

            # Location data
            address_data = review_dict['itemReviewed']['address']
            address_country = address_data['addressCountry']
            address_city = address_data['addressLocality']
            address_state = address_data['addressRegion']
            address_zip_code = address_data['postalCode']
            street_address = address_data['streetAddress']
            full_address = f"{street_address}, {address_city}, {address_state} {address_zip_code}"
            
            coordinates = review_dict['itemReviewed']['geo']
            latitude = coordinates['latitude']
            longitude = coordinates['longitude']
            
            resto_reviews.append(
                {
                    'resto_name': resto_name,
                    'review': just_review,
                    'food_rundown': food_rundown,
                    'cuisine': review_cuisine,
                    'perfect_for_tags': review_tags,
                    'price_range': review_price,
                    'review_date': review_date,
                    'resto_image': resto_image_url,
                    'resto_website': website_url,
                    'resto_neighborhood': neighborhood,
                    'city': city,
                    'address_country': address_country,
                    'address_city': address_city,
                    'address_state': address_state,
                    'address_zip_code': address_zip_code,
                    'street_address': street_address,
                    'full_address': full_address,
                    'latitude': latitude,
                    'longitude': longitude
                }
            )

            print(f"Got review for {resto_name}! Parsed {count + 1} restaurants so far.")
            sleep_time = random.randint(1, 3)
            print(f"Sleeping for {sleep_time} secs.... Let... Him.. Cook.")
            time.sleep(sleep_time)
        except Exception as e:
            print(f"Exception while processing URL {url}: {e}")
        

    output_file_name = f'infatuation_reviews_v7_{city}'
    # Write infatuation restaurant reviews to pkl and json file
    with open(f'{output_file_name}.pkl', 'wb') as file:
        pickle.dump(resto_reviews, file, protocol=pickle.HIGHEST_PROTOCOL)
    with open(f'{output_file_name}.json', 'w') as file:
        json.dump(resto_reviews, file)
    print(f"Dumped reviews to {output_file_name}.pkl and {output_file_name}.json files!")