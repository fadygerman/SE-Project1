from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from database import get_db
from models.db_models import Booking as BookingModel
from models.models import Booking

router = APIRouter(
    prefix="/bookings",
    tags=["bookings"]
)

# Get all bookings endpoint
@router.get("/", response_model=List[Booking])
async def get_bookings(db: Session = Depends(get_db)):
    bookings = db.query(BookingModel).all()
    return bookings

# Get booking by ID endpoint
@router.get("/{booking_id}", response_model=Booking)
async def get_booking(booking_id: int, db: Session = Depends(get_db)):
    booking = db.query(BookingModel).filter(BookingModel.id == booking_id).first()
    if booking is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Booking with ID {booking_id} not found"
        )
    return booking