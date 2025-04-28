from decimal import Decimal
from pydantic import BaseModel, ConfigDict, Field, field_validator


class Car(BaseModel):
    id: int
    name: str = Field(description="Car name/brand")
    model: str = Field(description="Car model")
    price_per_day: Decimal = Field(description="Daily rental price", gt=0)
    is_available: bool = Field(description="Whether the car is available for booking")
    latitude: float | None = Field(None, description="Car's current latitude location")
    longitude: float | None = Field(None, description="Car's current longitude location")
    
    model_config = ConfigDict(from_attributes=True)
    
    @field_validator('price_per_day')
    @classmethod
    def validate_price(cls, v):
        if v <= 0:
            raise ValueError('Price must be greater than zero')
        return v
    
