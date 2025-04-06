from datetime import date, time, timedelta
from decimal import Decimal
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field, ConfigDict, field_validator

from models.pydantic.car import Car
from models.pydantic.user import User

class BookingStatus(str, Enum):
    PLANNED = "PLANNED"
    ACTIVE = "ACTIVE"
    COMPLETED = "COMPLETED"
    CANCELED = "CANCELED"
    OVERDUE = "OVERDUE"
    
class Booking(BaseModel):
    id: int
    user_id: int = Field(description="ID of the user making the booking")
    car_id: int = Field(description="ID of the car being booked")
    start_date: date = Field(description="Start date of the booking period")
    end_date: date = Field(description="End date of the booking period")
    planned_pickup_time: time = Field(description="Time when the car will be picked up on start_date (UTC time)")
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
    planned_pickup_time: time = Field(description="Time when the car will be picked up on start_date (UTC time)")
    
    @field_validator('start_date')
    @classmethod
    def validate_start_date(cls, start_date):
        if start_date is None:
            raise ValueError('Start date is required')
        
        # Ensure start_date is at least tomorrow (today + 1 day)
        tomorrow = date.today() + timedelta(days=1)
        if start_date < tomorrow:
            raise ValueError('Start date must be tomorrow or later')
        
        return start_date
    
    @field_validator('end_date')
    @classmethod
    def validate_end_date(cls, end_date, info):
        if end_date is None:
            raise ValueError('End date is required')
            
        start_date = info.data.get('start_date')
        if start_date and end_date < start_date:
            raise ValueError('End date must be after start date')
        return end_date
    
    @field_validator('planned_pickup_time')
    @classmethod
    def validate_planned_pickup_time(cls, planned_pickup_time):
        if planned_pickup_time is None:
            raise ValueError('Planned pickup time is required')
        # Time is treated as UTC time without timezone information
        return planned_pickup_time
    
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