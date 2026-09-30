from typing import Optional
from pydantic import BaseModel, Field, EmailStr

class RegisterRequest(BaseModel):
    name: str = Field(min_length=2, max_length=80)
    email: EmailStr
    password: str = Field(min_length=6, max_length=100)

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class HomeRequest(BaseModel):
    budget: float = Field(gt=0)
    room_type: str
    style: str = "Modern"
    items: str = ""
    notes: str = ""

class PartyRequest(BaseModel):
    budget: float = Field(gt=0)
    guests: int = Field(gt=0)
    event_type: str
    venue: str = ""
    preferences: str = ""

class JewelryRequest(BaseModel):
    budget: float = Field(gt=0)
    occasion: str
    style: str = "Elegant"
    outfit_description: str = ""
