from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from database import get_db
from models.db_models import Booking as BookingModel, Car as CarModel, BookingStatus
from models.models import Booking, BookingCreate

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

@router.post("/", response_model=Booking, status_code=status.HTTP_201_CREATED)
async def create_booking(booking: BookingCreate, db: Session = Depends(get_db)):
    # Check if car exists
    car = db.query(CarModel).filter(CarModel.id == booking.car_id).first()
    if not car:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Car with ID {booking.car_id} not found"
        )
    
    # Check if car is available
    if not car.is_available:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Car with ID {booking.car_id} is not available for booking"
        )
    
    # Check for overlapping bookings
    overlapping_bookings = db.query(BookingModel).filter(
        BookingModel.car_id == booking.car_id,
        BookingModel.status.in_([BookingStatus.PLANNED, BookingStatus.ACTIVE]),
        BookingModel.start_date <= booking.end_date,
        BookingModel.end_date >= booking.start_date
    ).first()
    
    if overlapping_bookings:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="The car is already booked for the selected dates"
        )
    
    # Calculate booking duration in days
    delta = (booking.end_date - booking.start_date).days
    if delta < 1:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Booking must be for at least 1 day"
        )
    
    # Calculate total cost
    total_cost = car.price_per_day * delta
    
    # Create new booking
    new_booking = BookingModel(
        user_id=booking.user_id,
        car_id=booking.car_id,
        start_date=booking.start_date,
        end_date=booking.end_date,
        total_cost=total_cost,
        status=BookingStatus.PLANNED
    )
    
    # Add to database
    db.add(new_booking)
    db.commit()
    db.refresh(new_booking)
    
    return new_booking