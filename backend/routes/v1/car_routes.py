from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from database import get_db
from exceptions.cars import CarNotFoundException
from exceptions.currencies import CurrencyServiceUnavailableException, InvalidCurrencyException
from models.currencies import Currency
from models.pydantic.car import Car
from models.pydantic.pagination import PaginationParams, SortParams, PaginatedResponse
from services import car_service
from services.auth_service import get_current_user

router = APIRouter(
    prefix="/cars",
    tags=["cars"]
)

# Get all cars endpoint with pagination, filtering and sorting
@router.get("/", response_model=PaginatedResponse[Car])
async def get_cars(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(10, ge=1, le=100, description="Number of items per page"),
    name: str | None = Query(None, description="Filter by car name or model"),
    available_only: bool = Query(False, description="Show only available cars"),
    sort_by: str = Query("id", description="Field to sort by"),
    sort_order: str = Query("asc", description="Sort order (asc or desc)"),
    currency_code: Annotated[
        str, 
        Query(
            description="Currency code to convert prices to", 
            enum=[currency.value for currency in Currency]
        )
    ] = Currency.USD.value,
    db: Session = Depends(get_db),
    _=Depends(get_current_user)  # Require authentication
):
    """
    Get all cars with filtering, sorting and pagination.
    """
    try:
        pagination = PaginationParams(page=page, page_size=page_size)
        sort_params = SortParams(sort_by=sort_by, sort_order=sort_order)
        
        return car_service.get_filtered_cars(
            db, pagination, name_filter=name, available_only=available_only, 
            currency_code=currency_code, sort_params=sort_params
        )
    except InvalidCurrencyException as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=e.message
        )
    except CurrencyServiceUnavailableException as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=e.message
        )

# Get car by ID endpoint
@router.get("/{car_id}", response_model=Car)
async def get_car(
    car_id: int, 
    currency_code: Annotated[
        str, 
        Query(
            description="Currency code to convert price to", 
            enum=[currency.value for currency in Currency]
        )
    ] = Currency.USD.value,
    db: Session = Depends(get_db),
    _=Depends(get_current_user)  # Require authentication
):
    try:
        return car_service.get_car_by_id(car_id, db, currency_code)
    except CarNotFoundException as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=e.message
        )
    except InvalidCurrencyException as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=e.message
        )
    except CurrencyServiceUnavailableException as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=e.message
        )