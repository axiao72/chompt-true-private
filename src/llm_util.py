from langchain.embeddings import HuggingFaceEmbeddings
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.chat_models import ChatOpenAI
from langchain.llms import OpenAI
from langchain.chains.llm import LLMChain
from langchain.text_splitter import CharacterTextSplitter, RecursiveCharacterTextSplitter
from langchain.schema.document import Document
from langchain.prompts import PromptTemplate
from typing import List
from langchain.output_parsers import PydanticOutputParser
from langchain.pydantic_v1 import BaseModel as LangchainBaseModel, Field, validator
from src.prompts import *
import sys
import os


class Restaurant(LangchainBaseModel):
    # Pydantic class for extracting entities using LLM
    cuisine: List[str] = Field(description="List of cuisines of a restaurant")
    neighborhood: List[str] = Field(description="List of neighborhoods a restaurant is located in")


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
    # print(f"Using prompt: {extract_input.to_string()}", file=sys.stderr)
    try:
        output = llm(extract_input.to_string())
        filters = parser.parse(output)
        # metadata_filter = {} # Pinecone filter
        pre_metadata_filter = {'$and':[]} # Mongo filter
        post_metadata_filter = {} # Just plain dictionary to format later
        if filters.cuisine:
            # Mongo filter
            pre_metadata_filter['$and'].append(
                {
                    'cuisine': {"$in": [i.lower() for i in filters.cuisine]}
                }
            )
            post_metadata_filter['cuisine'] = [i.lower() for i in filters.cuisine]
            # metadata_filter['cuisine'] = {"$in": [filters.cuisine.lower()]} # Pinecone filter
        if filters.neighborhood:
            # Mongo filter
            pre_metadata_filter['$and'].append(
                {
                    'neighborhood': {"$in": [i.lower() for i in filters.neighborhood]}
                }
            )
            post_metadata_filter['neighborhood'] = [i.lower() for i in filters.neighborhood]

            # metadata_filter['neighborhood'] = {"$in": [filters.neighborhood.lower()]} # Pinecone filter
    except Exception as e:
        print(f"Exception while extracting cuisine and neighborhood: {e}", file=sys.stderr)
        pre_metadata_filter = {'$and':[]} # Keep empty if exception happens so recommendation can continue without filters
        post_metadata_filter = {}
    return pre_metadata_filter, post_metadata_filter


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