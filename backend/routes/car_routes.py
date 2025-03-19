from fastapi import APIRouter, HTTPException, status
from typing import List
from models.models import Car

router = APIRouter(
    prefix="/cars",
    tags=["cars"]
)

# Sample data - will be replaced with database later
cars_db = [
    {
        "id": 1,
        "name": "Toyota",
        "model": "Corolla",
        "price_per_day": 45.0,
        "is_available": True,
        "latitude": 35.6895,
        "longitude": 139.6917
    },
    {
        "id": 2,
        "name": "Honda",
        "model": "Civic",
        "price_per_day": 50.0,
        "is_available": False,
        "latitude": 34.0522,
        "longitude": -118.2437
    },
    {
        "id": 3,
        "name": "Ford",
        "model": "Mustang",
        "price_per_day": 75.0,
        "is_available": True,
        "latitude": 51.5074,
        "longitude": -0.1278
    },
    {
        "id": 4,
        "name": "Chevrolet",
        "model": "Camaro",
        "price_per_day": 70.0,
        "is_available": True,
        "latitude": 40.7128,
        "longitude": -74.0060
    },
    {
        "id": 5,
        "name": "Tesla",
        "model": "Model 3",
        "price_per_day": 100.0,
        "is_available": False,
        "latitude": 37.7749,
        "longitude": -122.4194
    }
]

# Get all cars endpoint
@router.get("/", response_model=List[Car])
async def get_cars():
    return cars_db

# Get car by ID endpoint
@router.get("/{car_id}", response_model=Car)
async def get_car(car_id: int):
    for car in cars_db:
        if car["id"] == car_id:
            return car
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"Car with ID {car_id} not found"
    )