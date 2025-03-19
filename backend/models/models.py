from decimal import Decimal
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