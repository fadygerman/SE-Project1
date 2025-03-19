from fastapi import APIRouter, HTTPException, status
from typing import List
from datetime import date
from models.models import Booking, BookingStatus

router = APIRouter(
    prefix="/bookings",
    tags=["bookings"]
)

# Sample data
bookings_db = [
    {
        "id": 1,
        "user_id": 1,
        "car_id": 3,
        "start_date": date(2025, 4, 1),
        "end_date": date(2025, 4, 5),
        "total_cost": 375.0,
        "status": BookingStatus.ACTIVE
    },
    {
        "id": 2,
        "user_id": 2,
        "car_id": 1,
        "start_date": date(2025, 3, 15),
        "end_date": date(2025, 3, 20),
        "total_cost": 225.0,
        "status": BookingStatus.COMPLETED
    }
]

# Get all bookings endpoint
@router.get("/", response_model=List[Booking])
async def get_bookings():
    return bookings_db

# Get booking by ID endpoint
@router.get("/{booking_id}", response_model=Booking)
async def get_booking(booking_id: int):
    for booking in bookings_db:
        if booking["id"] == booking_id:
            return booking
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"Booking with ID {booking_id} not found"
    )