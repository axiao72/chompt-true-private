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
from langchain.llms import OpenAI
from langchain.chains.llm import LLMChain
from langchain.vectorstores import Pinecone
from langchain.text_splitter import CharacterTextSplitter, RecursiveCharacterTextSplitter
from langchain.schema.document import Document
from langchain.prompts import PromptTemplate
from langchain.output_parsers import PydanticOutputParser
from langchain.pydantic_v1 import BaseModel as LangchainBaseModel, Field, validator
from datetime import datetime
import os
import sys
# from dotenv import load_dotenv
from tqdm.auto import tqdm
from uuid import uuid4
import sys
from src.prompts import *


# load_dotenv()
class Restaurant(LangchainBaseModel):
    # Pydantic class for extracting entities using LLM
    cuisine: str = Field(description="cuisine of a restaurant")
    neighborhood: str = Field(description="neighborhood a restaurant is located in")


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


def extract_entities(query: str, openai_api_key):
    # Extract cuisine and/or neighborhood to use as metadata filters
    llm = OpenAI(
    openai_api_key=openai_api_key,
    temperature=0, 
    model="text-davinci-003"
    )

    parser = PydanticOutputParser(pydantic_object=Restaurant)
    pydantic_prompt = PromptTemplate(
        template=PYDANTIC_TEMPLATE,
        input_variables=['query'],
        partial_variables={"format_instructions": parser.get_format_instructions()},
    )

    extract_input = pydantic_prompt.format_prompt(query=query)
    output = llm(extract_input.to_string())
    filters = parser.parse(output)
    metadata_filter = {}
    if filters.cuisine:
        # Change metadata to lower() and then use lower() for this instead of title()
        metadata_filter['cuisine'] = {"$in": [filters.cuisine.title()]}
    if filters.neighborhood:
        metadata_filter['neighborhood'] = {"$in": [filters.neighborhood.lower()]}
    return metadata_filter


def get_top_restos(query: str, embed_model: HuggingFaceEmbeddings, index, metadata_filters):
    embedded_query = embed_model.embed_query(query)
    # vector_store = Pinecone.from_existing_index(index_name, embed_model)
    # Restos are returned containing appropriate metadata and reviews
    if metadata_filters:
        print(f"Searching vector database with metadata filters: {metadata_filters}..." , file=sys.stderr)
        top_restos = index.query(
            vector=embedded_query,
            filter=metadata_filters,
            top_k=3,
            include_metadata=True
        )['matches']
        if len(top_restos) == 0:
            print(f"Metadata filter search returned no results. Re-running vector database search with no metadata filters..." , file=sys.stderr)
            top_restos = index.query(vector=embedded_query, top_k=3, include_metadata=True)['matches']
    else:
        print(f"Searching vector database with no metadata filters..." , file=sys.stderr)
        top_restos = index.query(vector=embedded_query, top_k=3, include_metadata=True)['matches']
    # Get actual resto data from matches key
    print("Found the top 3 restaurants!! Watch out... their spppiiiicccyyyyyyy...", file=sys.stderr)
    for i in top_restos:
        print(f"{i.metadata['resto_name']} similarity search score: {i.score}\n")
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


