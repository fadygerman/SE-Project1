'''
Pydantic models, provided by the Pydantic library 
(a data validation and settings management library in Python), 
are used to validate incoming data, serialize outgoing data, 
and define the structure of the data used in the application.
'''

from datetime import date
from decimal import Decimal
from enum import Enum
from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator
from typing import Optional

class BookingStatus(str, Enum):
    PLANNED = "PLANNED"
    ACTIVE = "ACTIVE"
    COMPLETED = "COMPLETED"
    CANCELED = "CANCELED"
    OVERDUE = "OVERDUE"

# Response models (output)    
class User(BaseModel):
    id: int
    first_name: str = Field(description="User's first name", min_length=1, max_length=50)
    last_name: str = Field(description="User's last name", min_length=1, max_length=50) 
    email: EmailStr = Field(description="User's email address")
    phone_number: str = Field(description="User's phone number")
    password_hash: Optional[str] = Field(None, description="Hashed password (internal use only)", exclude=True)
    
    model_config = ConfigDict(from_attributes=True)
    
    @field_validator('phone_number')
    @classmethod
    def validate_phone(cls, v):
        # Basic phone validation - can be enhanced based on your specific requirements
        if not v or len(v) < 8:
            raise ValueError('Phone number must be at least 8 characters')
        return v

class Car(BaseModel):
    id: int
    name: str = Field(description="Car name/brand")
    model: str = Field(description="Car model")
    price_per_day: Decimal = Field(description="Daily rental price", gt=0)
    is_available: bool = Field(description="Whether the car is available for booking")
    latitude: Optional[float] = Field(None, description="Car's current latitude location")
    longitude: Optional[float] = Field(None, description="Car's current longitude location")
    
    model_config = ConfigDict(from_attributes=True)
    
    @field_validator('price_per_day')
    @classmethod
    def validate_price(cls, v):
        if v <= 0:
            raise ValueError('Price must be greater than zero')
        return v
    
class Booking(BaseModel):
    id: int
    user_id: int = Field(description="ID of the user making the booking")
    car_id: int = Field(description="ID of the car being booked")
    start_date: date = Field(description="Start date of the booking period")
    end_date: date = Field(description="End date of the booking period")
    pickup_date: Optional[date] = Field(None, description="Actual date when car was picked up")
    return_date: Optional[date] = Field(None, description="Actual date when car was returned")
    total_cost: Decimal = Field(description="Total cost of the booking", gt=0)
    status: BookingStatus = Field(description="Current status of the booking")
    
    # Optional nested objects for full data retrieval
    user: Optional[User] = Field(None, description="User information")
    car: Optional[Car] = Field(None, description="Car information")
    
    model_config = ConfigDict(from_attributes=True)
    
    @field_validator('end_date')
    @classmethod
    def validate_dates(cls, end_date, info):
        start_date = info.data.get('start_date')
        if start_date and end_date < start_date:
            raise ValueError('End date must be after start date')
        return end_date
    
    @field_validator('return_date')
    @classmethod
    def validate_return_date(cls, return_date, info):
        pickup_date = info.data.get('pickup_date')
        if pickup_date and return_date and return_date < pickup_date:
            raise ValueError('Return date must be after pickup date')
        return return_date
    
# Request models (input)
class BookingCreate(BaseModel):
    user_id: int = Field(description="ID of the user making the booking")
    car_id: int = Field(description="ID of the car being booked")
    start_date: date = Field(description="Start date of the booking period")
    end_date: date = Field(description="End date of the booking period")
    
    @field_validator('end_date')
    @classmethod
    def validate_dates(cls, end_date, info):
        start_date = info.data.get('start_date')
        if start_date and end_date < start_date:
            raise ValueError('End date must be after start date')
        return end_date
    
class BookingUpdate(BaseModel):
    start_date: Optional[date] = Field(None, description="Updated start date")
    end_date: Optional[date] = Field(None, description="Updated end date") 
    status: Optional[BookingStatus] = Field(None, description="Updated booking status")
    pickup_date: Optional[date] = Field(None, description="Actual date when car was picked up")
    return_date: Optional[date] = Field(None, description="Actual date when car was returned")
    
    model_config = ConfigDict(from_attributes=True)
    
    @field_validator('end_date')
    @classmethod
    def validate_dates(cls, end_date, info):
        if end_date is None:
            return end_date
            
        start_date = info.data.get('start_date')
        if start_date is None:
            # If start_date not provided in update, we'll need to check against existing booking
            return end_date
            
        if end_date < start_date:
            raise ValueError('End date must be after start date')
        return end_date
        
    @field_validator('return_date')
    @classmethod
    def validate_return_date(cls, return_date, info):
        if return_date is None:
            return return_date
            
        pickup_date = info.data.get('pickup_date')
        if pickup_date is None:
            # If pickup_date not provided in update, we'll need to check against existing booking
            return return_date
            
        if return_date < pickup_date:
            raise ValueError('Return date must be after pickup date')
        return return_date
    
class UserRegister(BaseModel):
    first_name: str = Field(description="User's first name", min_length=1, max_length=50)
    last_name: str = Field(description="User's last name", min_length=1, max_length=50)
    email: EmailStr = Field(description="User's email address")
    phone_number: str = Field(description="User's phone number")
    password: str = Field(description="User's password", min_length=8)
    
    @field_validator('phone_number')
    @classmethod
    def validate_phone(cls, v):
        if not v or len(v) < 8:
            raise ValueError('Phone number must be at least 8 characters')
        return v
    
    @field_validator('password')
    @classmethod
    def validate_password(cls, v):
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters')
        # Add more password validation as needed (special chars, numbers, etc.)
        return v