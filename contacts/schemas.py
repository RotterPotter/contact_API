from pydantic import BaseModel
import pydantic
from datetime import date
from pydantic_extra_types.phone_numbers import PhoneNumber

class Contact(BaseModel):
    firstname: str
    lastname: str
    email: pydantic.EmailStr
    phone: PhoneNumber
    birthday: date

class PostContact(Contact):
    pass