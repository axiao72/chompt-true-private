from pydantic import BaseModel
from typing import List, Optional
from langchain_core.pydantic_v1 import BaseModel as LangchainBaseModel


class IdealMeal(BaseModel):
    description: str
    city: str
    # Optional fields, only used when reservation mode is on
    res_mode_on: bool = False
    res_date: str = None  # 'YYYY-MM-DD'
    res_time: str = None  # eg. '19:00' (7:00 pm)
    party_size: int = None
    # Optional, defaults to 'guest'
    username: str = 'chompt_guest'


class User(BaseModel):
    username: str
    password: str
    first_name: str
    last_name: str


class LoginCredentials(BaseModel):
    username: str
    password: str


class Event(BaseModel):
    event: str
    name: str
    value: str
    date: str
    username: str
    user_city: str


class Restaurant(LangchainBaseModel):
    cuisine: Optional[List[str]]
    location: Optional[List[str]]