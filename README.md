# CHOMPT
Full-stack Semantic Restaurant Chooser

## Gist
A lot of restaurant apps/search engines like Yelp, Beli, and Google are good for browsing different restaurants, but only to an extent. They're good for sifting through restaurants that fit easily categorized criteria, such as cuisine, price range, location, etc. However, they lack the capability to match restaurants to the more semantic descriptions and thoughts that one usually wants to base their decision of where to eat on. 

For example, I OFTEN find myself in the situation where I'm trying to think of a restaurant that would be good for a group of around 6-8 friends on a Friday night before going out, has a fun vibe, plays fire music, and serves cheap drinks and superb food. Already, we've pretty much left the realm of helpfulness that Yelp and Google could provide without sifting through restaurants for hours. 

This is where this webapp steps in. The following is the basic outline of this idea:
- Scrape the web for restuarant reviews (from journals like infatuation, eater, conde nast, etc.)
- Convert these reviews into embeddings and store them in a vector database (Pinecone) with various metadata (restaurant name, price range, perfect-for tags, etc). Now, we have a rich database of detailed, professional reviews from my personal favorite journals (that I heavily trust and rely on on a daily basis anyway) that we can search for restaurants on.
- Ask the user to literally describe what they envision for their dinner (could expand to night out and include bars), take their description, and do a similarity search on the embeddings we have in our vector db. We can also set filters on our search using the metadata if the user provides any categorical criteria they'd like to apply.
- Return 3 restaurants. This also eliminates the possibility of going down the rabbit hole of potential restaurants to choose from, which I do almost weekly on Yelp, Beli, etc. 

Yes, ChatGPT can probably already do this, but only includes restaurants that are open up to the date of model training, which could exclude many new restaurants. And this is my own idea and implementation so it's cooler.

There's many other parts to the idea that I'm not including for simplicity sake, and because I want to get this basic foundation going first.

Let's see where we go 🫡

## Heads Up
This is an ongoing project so it's VERY barebones, but will be improving every day! For example, one major thing you'll probably notice is that restaurants are repeated in recommendations. Do not fret! I'm using a miniscule set of data (only about 250 restaurants) so that will improve when I gather more data. A lot of things are just placeholders while I figure out everything else. Thanks for your understanding, I promise it'll be worth it.

## Getting Started! 
### As this repo is changing daily, these instructions will most likely be outdated. Live URL to access the application directly: https://seashell-app-tdlgj.ondigitalocean.app/
### Installation
1. Clone the repo
2. Create a fresh virtual environment (conda or whatever Python venv you want to use)
3. `cd` into the repo root
4. Run `npm install`
5. Run `npm audit fix --force` (these are janky installs i know, chill i'm still learning front end)
6. Run `pip install -r requirements.txt`
### Environment Variables
1. Create a .env file in the repo root with the following variables:
```
OPENAI_API_KEY=''
PINECONE_API_KEY=''
PINECONE_ENVIRONMENT=''
PINECONE_INDEX_NAME=''
```
#### OpenAI
1. If you haven't already, create an OpenAI account (https://openai.com/) (Skip to step 4 if you already have an OpenAPI key)
2. Navigate to their API platform and go to API keys on the left-side menu (https://platform.openai.com/api-keys)
3. Create a new secret key and copy it (You won't be able to see it again after closing out the window, so make sure it's nice and copied)
4. Add your OpenAI key to the `OPENAI_API_KEY=` variable in your .env file
#### Pinecone (Cloud Vector Database)
1. Create a Pinecone account (https://www.pinecone.io/)
2. Create an Index. The name you use will be the name you add to `PINECONE_INDEX_NAME=` in your .env file. Also, make sure to put 1024 in the dimensions field (this is the dimensions of the embeddings model the app uses) and use cosine for the metric field. Click Create Index.
3. Add your Pinecone API Key and Environment name to your .env file as well (`PINECONE_API_KEY=''` and `PINECONE_ENVIRONMENT=''`) 
### Running the app!
1. Run `npm run dev` (FastAPI will run on http://127.0.0.1:8000)
2. After the api server is up and running (might take a few seconds), navigate to http://localhost:3000 to use the app
3. Click the About button in the top right corner of the UI and read how it works
4. Enjoy! 😋🍴


