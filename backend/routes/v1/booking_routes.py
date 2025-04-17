from typing import List

from fastapi import APIRouter, Body, Depends, HTTPException, status
from sqlalchemy.orm import Session

from database import get_db
from exceptions.bookings import *
from models.db_models import Booking as BookingDB
from models.db_models import User, UserRole
from models.pydantic.booking import Booking, BookingCreate, BookingUpdate
from services import booking_service
from services.auth_service import get_booking_with_permission_check, get_current_user, require_role

router = APIRouter(
    prefix="/bookings",
    tags=["bookings"]
)

# Get all bookings endpoint - admin only
@router.get("/", response_model=List[Booking])
async def get_bookings(
    db: Session = Depends(get_db), 
    _=Depends(require_role([UserRole.ADMIN]))
):
    bookings = db.query(BookingDB).all()
    return bookings

# Get user's own bookings
@router.get("/my", response_model=List[Booking])
async def get_my_bookings(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all bookings for the currently authenticated user"""
    bookings = db.query(BookingDB).filter(BookingDB.user_id == current_user.id).all()
    return bookings

@router.get("/{booking_id}", response_model=Booking)
async def get_booking(
    booking: BookingDB = Depends(get_booking_with_permission_check)
):
    """Get booking by ID. Users can only access their own bookings unless they are admins."""
    return booking

@router.post("/", response_model=Booking, status_code=status.HTTP_201_CREATED)
async def create_booking(
    booking_data: BookingCreate, 
    db: Session = Depends(get_db), 
    current_user: User = Depends(get_current_user)
):
    
    try:
        return booking_service.create_booking(booking_data, current_user.id, db)
    except NoCarFoundException as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=e.message
        )
    
    except (
        CarNotAvailableException,
        BookingOverlapException,
    ) as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=e.message
        )    

@router.put("/{booking_id}", response_model=Booking)
async def update_booking(
    booking: BookingDB = Depends(get_booking_with_permission_check),
    booking_update: BookingUpdate = Body(...),
    db: Session = Depends(get_db)
):
    """Update a booking. Users can only update their own bookings unless they are admins."""
    try:
        # Pass the booking ID from the retrieved booking object
        return booking_service.update_booking(booking.id, booking_update, db)
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