from pydantic import BaseModel


class IdealMeal(BaseModel):
    description: str
    # Optional fields, only used when reservation mode is on
    res_mode_on: bool = False
    res_date: str = None  # 'YYYY-MM-DD'
    res_time: str = None  # eg. '19:00' (7:00 pm)
    party_size: int = None
    # Optional, defaults to 'guest'
    username: str = 'guest'

class User(BaseModel):
    username: str
    password: str
    first_name: str
    last_name: str

class LoginCredentials(BaseModel):
    username: str
    password: str