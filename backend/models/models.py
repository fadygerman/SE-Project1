from datetime import date
from decimal import Decimal
from enum import Enum
from pydantic import BaseModel
from typing import Optional

class Car(BaseModel):
    id: int
    name: str
    model: str
    price_per_day: Decimal
    is_available: bool
    latitude: Optional[float] = None
    longitude: Optional[float] = None

class BookingStatus(str, Enum):
    ACTIVE = "active"
    COMPLETED = "completed"
    CANCELED = "canceled"

class User(BaseModel):
    id: int
    first_name: str
    last_name: str
    email: str  # Change to EmailStr if you install email-validator package
    phone_number: str
    password_hash: Optional[str] = None  # Only for internal use, not in responses
    
class Booking(BaseModel):
    id: int
    user_id: int
    car_id: int
    start_date: date
    end_date: date
    total_cost: Decimal
    status: BookingStatus
    
    # Optional nested objects for full data retrieval
    user: Optional[User] = None
    car: Optional[Car] = None