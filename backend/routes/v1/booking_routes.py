from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from database import get_db
from models.db_models import Booking as BookingDB, User
from models.pydantic.booking import Booking, BookingCreate, BookingUpdate
from services import booking_service
from exceptions.bookings import *
from services.auth_service import get_current_user, require_role

router = APIRouter(
    prefix="/bookings",
    tags=["bookings"]
)

# Get all bookings endpoint - admin only
@router.get("/", response_model=List[Booking])
async def get_bookings(
    db: Session = Depends(get_db), 
    _=Depends(require_role(["admin"]))
):
    bookings = db.query(BookingDB).all()
    return bookings

# Get user's own bookings
@router.get("/my-bookings", response_model=List[Booking])
async def get_my_bookings(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all bookings for the currently authenticated user"""
    bookings = db.query(BookingDB).filter(BookingDB.user_id == current_user.id).all()
    return bookings

# Get booking by ID endpoint
@router.get("/{booking_id}", response_model=Booking)
async def get_booking(
    booking_id: int, 
    db: Session = Depends(get_db), 
    current_user: User = Depends(get_current_user)
):
    booking = db.query(BookingDB).filter(BookingDB.id == booking_id).first()
    if booking is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Booking with ID {booking_id} not found"
        )
    
    # Users can only access their own bookings unless they're admins
    if booking.user_id != current_user.id:
        # In a real app, you would check if the user has admin privileges
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only access your own bookings"
        )
        
    return booking

@router.post("/", response_model=Booking, status_code=status.HTTP_201_CREATED)
async def create_booking(
    booking_data: BookingCreate, 
    db: Session = Depends(get_db), 
    current_user: User = Depends(get_current_user)
):
    # Always use the authenticated user's ID for the booking
    booking_data.user_id = current_user.id
    
    try:
        return booking_service.create_booking(booking_data, db)
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
async def update_booking(
    booking_id: int, 
    booking_update: BookingUpdate, 
    db: Session = Depends(get_db), 
    current_user: User = Depends(get_current_user)
):
    # Verify the booking belongs to the current user
    booking = db.query(BookingDB).filter(BookingDB.id == booking_id).first()
    if booking and booking.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only update your own bookings"
        )
    
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