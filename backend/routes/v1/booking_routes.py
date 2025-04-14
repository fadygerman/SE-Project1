from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from database import get_db
from models.db_models import Booking as BookingDB
from models.pydantic.booking import Booking, BookingCreate, BookingUpdate

from services import booking_service
from exceptions.bookings import *

router = APIRouter(
    prefix="/bookings",
    tags=["bookings"]
)

# Get all bookings endpoint
@router.get("/", response_model=List[Booking])
async def get_bookings(db: Session = Depends(get_db)):
    bookings = db.query(BookingDB).all()
    return bookings

# Get booking by ID endpoint
@router.get("/{booking_id}", response_model=Booking)
async def get_booking(booking_id: int, db: Session = Depends(get_db)):
    booking = db.query(BookingDB).filter(BookingDB.id == booking_id).first()
    if booking is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Booking with ID {booking_id} not found"
        )
    return booking

@router.post("/", response_model=Booking, status_code=status.HTTP_201_CREATED)
async def create_booking(booking: BookingCreate, db: Session = Depends(get_db)):
    try:
        return booking_service.create_booking(booking, db)
    except NoCarFoundException as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=e.message
        )
    
    except (
        CarNotAvailableException,
        BookingOverlapException,
        BookingStartDateException
    ) as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=e.message
        )    

@router.put("/{booking_id}", response_model=Booking)
async def update_booking(booking_id: int, booking_update: BookingUpdate, db: Session = Depends(get_db)):
    try:
        return booking_service.update_booking(booking_id, booking_update, db)
    except BookingNotFoundException as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=e.message
        )
    except (
        BookingStateException,
        DateRangeException, 
        BookingOverlapUpdateException,
        PickupAfterReturnException,
        FutureDateException,
        ReturnWithoutPickupException,
        DateOutsideBookingPeriodException
    ) as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=e.message
        )