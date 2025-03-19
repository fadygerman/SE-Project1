from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from database import get_db
from models.db_models import Car as CarModel
from models.models import Car

router = APIRouter(
    prefix="/cars",
    tags=["cars"]
)

# Get all cars endpoint
@router.get("/", response_model=List[Car])
async def get_cars(db: Session = Depends(get_db)):
    cars = db.query(CarModel).all()
    return cars

# Get car by ID endpoint
@router.get("/{car_id}", response_model=Car)
async def get_car(car_id: int, db: Session = Depends(get_db)):
    car = db.query(CarModel).filter(CarModel.id == car_id).first()
    if car is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Car with ID {car_id} not found"
        )
    return car