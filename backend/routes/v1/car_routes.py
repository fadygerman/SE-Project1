from typing import Annotated, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from database import get_db
from exceptions.cars import CarNotFoundException
from exceptions.currencies import InvalidCurrencyException
from models.currencies import Currency
from models.pydantic.car import Car
from services import car_service
from services.auth_service import get_current_user

router = APIRouter(
    prefix="/cars",
    tags=["cars"]
)

# Get all cars endpoint
@router.get("/", response_model=List[Car])
async def get_cars(
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
    try:
        return car_service.get_all_cars(db, currency_code)
    except InvalidCurrencyException as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
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
    current_user=Depends(get_current_user)  # Require authentication
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