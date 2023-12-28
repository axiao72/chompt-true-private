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


review_urls = []
for i in range(1, 150):
    try:
        url = f"https://www.theinfatuation.com/new-york/reviews?page={i}"
        page = urlopen(url)
        html = page.read().decode("utf-8")
        soup = BeautifulSoup(html, "html.parser")
        review_urls += [link['href'] for link in soup.html.select('a') if "/reviews/" in link['href']]
        print(f"Got review URL for page {i}")
        sleep_time = random.randint(1, 3)
        print(f"Sleeping for {sleep_time} secs.... Let... Him.. Cook.")
        time.sleep(sleep_time)
    except Exception as e:
        print(f"Exception while scraping infatuation! {e}")

already_scraped_urls = []
# with open('already_scraped_urls.txt', 'r') as file:
#     already_scraped_urls = file.read().splitlines()

# with open('already_scraped_urls.pkl', 'rb') as file:
#     already_scraped_urls = pickle.load(file)

resto_reviews = []

url_prefix = "https://www.theinfatuation.com"
for count, url in enumerate(tqdm(review_urls)):
    try:
        # Check if url was already scraped
        if url in already_scraped_urls:
            print("Already scraped restaurant from {url}")
            continue
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
                'resto_neighborhood': neighborhood
            }
        )

        already_scraped_urls.append(url)
        print(f"Got review for {resto_name}! Parsed {count + 1} restaurants so far.")
        sleep_time = random.randint(1, 3)
        print(f"Sleeping for {sleep_time} secs.... Let... Him.. Cook.")
        time.sleep(sleep_time)
    except Exception as e:
        print(f"Exception while processing URL {url}: {e}")
    
with open('already_scraped_urls.txt', 'w') as file:
    for item in already_scraped_urls:
        file.write(str(item) + '\n')
# with open('already_scraped_urls.pkl', 'wb') as file:
#     pickle.dump(already_scraped_urls, file, protocol=pickle.HIGHEST_PROTOCOL)

output_file_name = 'infatuation_reviews_v6'
# Write infatuation restaurant reviews to pkl and json file
with open(f'{output_file_name}.pkl', 'wb') as file:
    pickle.dump(resto_reviews, file, protocol=pickle.HIGHEST_PROTOCOL)
with open(f'{output_file_name}.json', 'w') as file:
    json.dump(resto_reviews, file)
print(f"Dumped reviews to {output_file_name}.pkl and {output_file_name}.json files!")