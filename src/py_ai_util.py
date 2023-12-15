from bs4 import BeautifulSoup
from urllib.request import urlopen
import json
# import requests
# import re
# import time
import pickle
import pinecone
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.chat_models import ChatOpenAI
from langchain.chains.llm import LLMChain
from langchain.vectorstores import Pinecone
from langchain.text_splitter import CharacterTextSplitter, RecursiveCharacterTextSplitter
from langchain.schema.document import Document
from langchain.prompts import PromptTemplate
from datetime import datetime
import os
import sys
# from dotenv import load_dotenv
from tqdm.auto import tqdm
from uuid import uuid4
import sys
from src.prompts import *


# load_dotenv()


def initialize_pinecone(api_key, environment):
    # Initialize Pinecone
    pinecone.init(
        api_key=api_key,
        environment=environment,
    )


def store_reviews(filename: str, embed_model: HuggingFaceEmbeddings, index_name):
    try:
        # If pinecone index already exists, delete and create new. 
        # Only using this function if want to create a new, updated index
        if index_name in pinecone.list_indexes():
            pinecone.delete_index(index_name)
            pinecone.create_index(
                    name=index_name,
                    metric='cosine',
                    dimension=1024 # 1024 dim of e5-large-v2
            )
        # Get Pinecone index
        index = pinecone.Index(index_name)
        # Get reviews from file
        with open(filename, 'rb') as file:
            resto_reviews = pickle.load(file)

        text_splitter = RecursiveCharacterTextSplitter(chunk_size=2500,
                                        chunk_overlap=800,
                                        length_function=len)
        
        # Chunk limit for upserting to Pinecone
        batch_limit = 30
        batch_count = 1

        upsert_chunks = []
        upsert_metadatas = []

        total_word_cnt = 0

        start_time = datetime.now()
        print(f"Start time: {start_time}", file=sys.stderr)
        # Split and prepare each review
        for i, resto in enumerate(tqdm(resto_reviews)):
            print(f"Chunking and preparing review #{i}...", file=sys.stderr)
            # Clean up review data
            cleaned_review = resto['review'].replace('&apos;', "'").replace("&amp;", "&").replace('&quot;', '"').replace("&quot", '"')
            cleaned_resto_name = resto['resto_name'].replace("&amp;", "&").replace('&apos;', "'")
            cleaned_resto_tags = resto['perfect_for_tags'].replace("&amp;", "&").replace('&apos;', "'")
            review_date = resto['review_date'].split('T')[0]
            
            # Set the metadata for this restaurant review
            metadata = {
                'resto_name': cleaned_resto_name,
                'cuisine': resto['cuisine'],
                'perfect_for_tags': cleaned_resto_tags,
                'price_range': resto['price_range'],
                'review_date': review_date,
                'image_url': resto['resto_image'],
            }
            # Split review into chunks
            review_chunks = text_splitter.split_text(cleaned_review)
            # Add the perfect-for tags and cuisine to the beginning of each review chunk so this becomes part of the embedding
            review_chunks = [f"Perfect for: {cleaned_resto_tags}. Serves {resto['cuisine']}. " + j for j in review_chunks]
            # Create metadata dicts for each chunk
            chunk_metadatas = [{
                "chunk": j, "text": text, **metadata
            } for j, text in enumerate(review_chunks)]
            # Append chunks to list of chunks (to be upserted to Pinecone)
            upsert_chunks.extend(review_chunks)
            # Append chunks metadatas to list of metadatas (also to be upserted to Pinecone)
            upsert_metadatas.extend(chunk_metadatas)
            # If we're at the batch_limit, store chunks in Pinecone
            if len(upsert_chunks) >= batch_limit:
                # Generate uuids for each chunk
                ids = [str(uuid4()) for _ in range(len(upsert_chunks))]
                # embed the chunks
                embeddings = embed_model.embed_documents(upsert_chunks)
                print(f"Batch full. Upserting dangerwich batch #{batch_count}...", file=sys.stderr)
                # Upsert the chunks
                index.upsert(vectors=zip(ids, embeddings, upsert_metadatas))
                print(f"Finished upserting dangerwich batch #{batch_count}!!!", file=sys.stderr)
                # Clear the batch of chunks and metadatas for the next batch
                upsert_chunks = []
                upsert_metadatas = []

        # If there are any left over chunks, upsert them
        if upsert_chunks:
            print("Upserting left over dangerwiches...", file=sys.stderr)
            ids = [str(uuid4()) for _ in range(len(upsert_chunks))]
            embeddings = embed_model.embed_documents(upsert_chunks)
            index.upsert(vectors=zip(ids, embeddings, upsert_metadatas))
        print("Finished upserting all dangerwiches... Broncos Country. Let's Ride.", file=sys.stderr)
        end_time = datetime.now()
        print(f"End time: {end_time}", file=sys.stderr)
        print(f"Total elapsed time: {end_time - start_time}", file=sys.stderr)
    except Exception as e:
        print(f"Exception occured while storing infatuation reviews in Pinecone: {e}", file=sys.stderr)


def get_top_restos(query: str, embed_model: HuggingFaceEmbeddings, index_name):
    vector_store = Pinecone.from_existing_index(index_name, embed_model)
    # Restos are returned as Langchain Documents, containing appropriate metadata and reviews
    print(f"Searching vector database..." , file=sys.stderr)
    top_restos = vector_store.similarity_search(query, k=3)
    print("Found the top 4 restaurants!! Watch out... their spppiiiicccyyyyyyy...", file=sys.stderr)
    return top_restos


def query_llm(restaurant_name: str, review: str, vision: str, openai_api_key):
    llm = ChatOpenAI(
        openai_api_key=openai_api_key,
        model_name='gpt-3.5-turbo',
        temperature=0.0
    )
    convince_prompt = PromptTemplate(
        template=CONVINCE_PROMPT_TEMPLATE,
        input_variables=['restaurant_name', 'review', 'vision']
    )
    convince_chain = LLMChain(llm=llm, prompt=convince_prompt)
    response = convince_chain(
        {
            "restaurant_name": restaurant_name,
            "review": review,
            "vision": vision,
        },
        return_only_outputs=True
    )
    return response.get('text')


def instantiate_embed_model(model_name: str, model_type: str):
    if model_type == 'OpenAI':
        embed_model = OpenAIEmbeddings(
                    document_model_name=model_name,
                    query_model_name=model_name,
                    openai_api_key=os.getenv('OPENAI_API_KEY')
                )
    elif model_type.lower() == 'hf':
        # Initialize e5-large-v2 embeddings model
        model_kwargs = {'device': 'cpu'}
        encode_kwargs = {'normalize_embeddings': False}

        embed_model = HuggingFaceEmbeddings(model_name=model_name,
                                            model_kwargs=model_kwargs,
                                            encode_kwargs=encode_kwargs)
    return embed_model


