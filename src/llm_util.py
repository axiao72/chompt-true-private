from langchain.chains import LLMChain, create_extraction_chain_pydantic
from langchain.prompts import PromptTemplate
from langchain.prompts.chat import (
    ChatPromptTemplate,
    HumanMessagePromptTemplate,
    SystemMessagePromptTemplate,
)
from langchain.schema import HumanMessage, SystemMessage
from langchain.output_parsers import PydanticOutputParser
from src.prompts import *
from src.constants import *
from api.pydantic_models import *
import sys
import os


def extract_filters(query: str) -> dict:
    filter_dict = {} # Just plain dictionary to format later
    try:
        # Extract cuisine and/or neighborhood to use as metadata filters
        chain = create_extraction_chain_pydantic(pydantic_schema=Restaurant, llm=CHAT_MODEL)
        filters = chain.run(query)[0] # Get index 0 because a list is returned and there should only be one object in the list
        if filters.cuisine:
            # Mongo filter
            filter_dict['cuisine'] = [i.lower() for i in filters.cuisine]
        if filters.location:
            # Mongo filter
            filter_dict['location'] = [i.lower() for i in filters.location]
    except Exception as e:
        print(f"Exception while extracting cuisine and neighborhood: {e}", file=sys.stderr)
        filter_dict = {}
    return filter_dict


def classify_location(location: str) -> str:
    try:
        # Prompts
        system_message_prompt = SystemMessagePromptTemplate.from_template(LOCATION_CLASSIFIER_TEMPLATE)
        human_template = "{text}"
        human_message_prompt = HumanMessagePromptTemplate.from_template(human_template)
        chat_prompt = ChatPromptTemplate.from_messages(
            [system_message_prompt, human_message_prompt]
        )
        # Classify location
        classified_response = CHAT_MODEL(
            chat_prompt.format_prompt(
                text=location
            ).to_messages()
        )
        return classified_response.content
    except Exception as ex:
        raise(f"Exception while classifying location: {ex}")


def query_llm(restaurant_name: str, review: str, vision: str):
    convince_prompt = PromptTemplate(
        template=CONVINCE_PROMPT_TEMPLATE,
        input_variables=['restaurant_name', 'review', 'vision']
    )
    convince_chain = LLMChain(llm=CHAT_MODEL, prompt=convince_prompt)
    response = convince_chain(
        {
            "restaurant_name": restaurant_name,
            "review": review,
            "vision": vision,
        },
        return_only_outputs=True
    )
    return response.get('text')