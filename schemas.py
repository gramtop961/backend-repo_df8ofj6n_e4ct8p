"""
Database Schemas

Define your MongoDB collection schemas here using Pydantic models.
These schemas are used for data validation in your application.

Each Pydantic model represents a collection in your database.
Model name is converted to lowercase for the collection name:
- User -> "user" collection
- Product -> "product" collection
- BlogPost -> "blogs" collection
"""

from pydantic import BaseModel, Field, EmailStr
from typing import Optional, Dict, Any
from datetime import date

# Core school info (optional persistence)
class School(BaseModel):
    name: str
    description: str
    mission: str
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    opening_hours: Optional[str] = None

# Advent registration schema
class AdventRegistration(BaseModel):
    parent_name: str = Field(..., description="Parent full name")
    child_name: str = Field(..., description="Child full name")
    phone: str = Field(..., description="Contact phone number")
    email: EmailStr = Field(..., description="Parent email address")
    consent: bool = Field(True, description="Processing consent")
    source: Optional[str] = Field("web", description="Registration source")

# Advent submission per day
class AdventSubmission(BaseModel):
    email: EmailStr
    day: int = Field(..., ge=1, le=24)
    answer: Optional[str] = None
    child_name: Optional[str] = None

# Generic notification log
class Notification(BaseModel):
    to_email: EmailStr
    subject: str
    template: str
    variables: Dict[str, Any] = {}

# Example schemas kept for reference (not used directly)
class User(BaseModel):
    name: str
    email: str
    address: str
    age: Optional[int] = None
    is_active: bool = True

class Product(BaseModel):
    title: str
    description: Optional[str] = None
    price: float
    category: str
    in_stock: bool = True
