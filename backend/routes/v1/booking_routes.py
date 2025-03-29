from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from datetime import date

from database import get_db
from models.db_models import Booking as BookingModel, Car as CarModel, BookingStatus
from models.models import Booking, BookingCreate, BookingUpdate

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

@router.put("/{booking_id}", response_model=Booking)
async def update_booking(booking_id: int, booking_update: BookingUpdate, db: Session = Depends(get_db)):
    # Get existing booking
    booking = db.query(BookingModel).filter(BookingModel.id == booking_id).first()
    if booking is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Booking with ID {booking_id} not found"
        )
    
    # Check if booking is in a state that allows updates
    if booking.status in [BookingStatus.COMPLETED, BookingStatus.CANCELED]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot update booking in {booking.status.value} state"
        )
    
    # Process date updates
    update_data = booking_update.model_dump(exclude_unset=True)
    
    # Handle status transitions with automatic date updates
    if 'status' in update_data:
        update_data['status'] = normalize_status(update_data['status'])
        new_status = update_data['status']
        # When transitioning to ACTIVE, set pickup_date to today if not provided
        if new_status == BookingStatus.ACTIVE and booking.status == BookingStatus.PLANNED:
            if 'pickup_date' not in update_data:
                update_data['pickup_date'] = date.today()
        
        # When transitioning to COMPLETED, set return_date to today if not provided
        if new_status == BookingStatus.COMPLETED and booking.status == BookingStatus.ACTIVE:
            if 'return_date' not in update_data:
                update_data['return_date'] = date.today()
    
    # Handle date validation if both dates are being updated
    if 'start_date' in update_data and 'end_date' in update_data:
        start_date = update_data['start_date']
        end_date = update_data['end_date']
        
        if end_date < start_date:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="End date must be after start date"
            )
    # Handle validation if only end_date is updated
    elif 'end_date' in update_data:
        if update_data['end_date'] < booking.start_date:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="End date must be after start date"
            )
    # Handle validation if only start_date is updated
    elif 'start_date' in update_data:
        if booking.end_date < update_data['start_date']:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="End date must be after start date"
            )
    
    # Check for overlapping bookings if dates are changed
    if 'start_date' in update_data or 'end_date' in update_data:
        start_date = update_data.get('start_date', booking.start_date)
        end_date = update_data.get('end_date', booking.end_date)
        
        overlapping_bookings = db.query(BookingModel).filter(
            BookingModel.car_id == booking.car_id,
            BookingModel.id != booking_id,  # Exclude the current booking
            BookingModel.status.in_([BookingStatus.PLANNED, BookingStatus.ACTIVE]),
            BookingModel.start_date <= end_date,
            BookingModel.end_date >= start_date
        ).first()
        
        if overlapping_bookings:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="The requested dates overlap with another booking"
            )
        
        # Recalculate total cost if dates change
        delta = (end_date - start_date).days
        if delta < 1:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Booking must be for at least 1 day"
            )
        
        car = db.query(CarModel).filter(CarModel.id == booking.car_id).first()
        update_data['total_cost'] = car.price_per_day * delta
    
    # Additional validation for pickup and return dates
    if 'pickup_date' in update_data and 'return_date' in update_data:
        if update_data['return_date'] < update_data['pickup_date']:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Return date must be after pickup date"
            )
    elif 'return_date' in update_data and booking.pickup_date:
        if update_data['return_date'] < booking.pickup_date:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Return date must be after pickup date"
            )
    elif 'pickup_date' in update_data and booking.return_date:
        if booking.return_date < update_data['pickup_date']:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Return date must be after pickup date"
            )
    
    # Validate pickup_date can't be in the future
    if 'pickup_date' in update_data:
        if update_data['pickup_date'] > date.today():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Pickup date cannot be in the future"
            )
        
        # Optionally: Auto-update status when pickup_date is set
        if booking.status == BookingStatus.PLANNED:
            update_data['status'] = BookingStatus.ACTIVE

    # Similar validation for return_date
    if 'return_date' in update_data:
        if update_data['return_date'] > date.today():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Return date cannot be in the future"
            )
        
        # Optionally: Auto-update status when return_date is set
        if booking.status == BookingStatus.ACTIVE:
            update_data['status'] = BookingStatus.COMPLETED
    
    # Ensure return_date cannot be set if pickup_date is null
    if 'return_date' in update_data and not booking.pickup_date and 'pickup_date' not in update_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot set return date without a pickup date"
        )

    # Ensure pickup_date is within booking period
    if 'pickup_date' in update_data:
        start_date = update_data.get('start_date', booking.start_date)
        end_date = update_data.get('end_date', booking.end_date)
        
        if update_data['pickup_date'] < start_date or update_data['pickup_date'] > end_date:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Pickup date must be within the booking period"
            )

    # Ensure return_date is within booking period
    if 'return_date' in update_data:
        start_date = update_data.get('start_date', booking.start_date)
        end_date = update_data.get('end_date', booking.end_date)
        
        if update_data['return_date'] < start_date or update_data['return_date'] > end_date:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Return date must be within the booking period"
            )
    
    # Update booking with new data
    for key, value in update_data.items():
        setattr(booking, key, value)
    
    # Save to database
    db.commit()
    db.refresh(booking)
    
    return booking

def normalize_status(status_value):
    """Convert any status format to the proper enum value"""
    if isinstance(status_value, BookingStatus):
        return status_value
        
    if isinstance(status_value, str):
        # Try to match case-insensitive
        for status in BookingStatus:
            if status.name.lower() == status_value.lower():
                return status
    
    return status_value
