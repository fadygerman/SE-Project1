from typing import Generic, TypeVar
from pydantic import BaseModel, Field, ConfigDict
from enum import Enum

T = TypeVar('T')

class SortOrder(str, Enum):
    ASC = "asc"
    DESC = "desc"

class PaginationParams(BaseModel):
    page: int = Field(1, description="Page number", ge=1)
    page_size: int = Field(10, description="Items per page", ge=1, le=100)

class SortParams(BaseModel):
    sort_by: str = Field("id", description="Field to sort by")
    sort_order: SortOrder = Field(SortOrder.ASC, description="Sort order (asc or desc)")
    
    model_config = ConfigDict(from_attributes=True)

class BookingFilterParams(BaseModel):
    status: str | None = None
    car_id: int | None = None
    start_date_from: str | None = None
    start_date_to: str | None = None
    end_date_from: str | None = None
    end_date_to: str | None = None
    
    model_config = ConfigDict(from_attributes=True)

class CarFilterParams(BaseModel):
    name: str | None = None
    available_only: bool = False
    
    model_config = ConfigDict(from_attributes=True)

class PaginatedResponse(BaseModel, Generic[T]):
    items: list[T]
    total: int
    page: int
    page_size: int
    pages: int
    
    model_config = ConfigDict(from_attributes=True)