from datetime import date
from decimal import Decimal
from typing import List, Optional

from fastapi import Depends, HTTPException, status
from sqlalchemy import and_, or_, desc, func
from sqlalchemy.orm import Session

import exceptions.bookings as booking_exceptions
from currency_converter.client import get_currency_converter_client_instance
from database import get_db
from models.db_models import Booking as BookingDB
from models.db_models import BookingStatus
from models.db_models import Car as CarDB
from models.db_models import User as UserDB
from models.db_models import UserRole
from models.pydantic.booking import Booking, BookingCreate, BookingUpdate
from models.pydantic.pagination import PaginationParams, BookingFilterParams, SortParams, PaginatedResponse
from models.pydantic.user import User
from services.auth_service import get_current_user


def get_all_bookings(db: Session) -> List[Booking]:
    bookings_db = db.query(BookingDB).all()
    bookings = []
    
    for booking_db in bookings_db:
        booking = Booking.model_validate(booking_db)
        booking.total_cost = convert_booking_currency(booking.total_cost, booking.exchange_rate)
        bookings.append(booking)
    
    return bookings

async def get_booking_with_permission_check(
    booking_id: int,
    db: Session = Depends(get_db),
    current_user_db: UserDB = Depends(get_current_user)
):
    """Check if the user has permission to access the specified booking"""
    from models.db_models import Booking as BookingDB
    
    try:
        booking_db = get_booking_by_id(booking_id, db)
    except booking_exceptions.BookingNotFoundException as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=e.message
        )
    
    booking = Booking.model_validate(booking_db)
    current_user = User.model_validate(current_user_db)
    # Check if it's the user's booking or if they have admin role
    if booking.user_id != current_user.id and current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, 
            detail="You can only access your own bookings"
        )
    
    return booking

def get_booking_by_id(booking_id: int, db: Session) -> Booking:
    booking_db = db.query(BookingDB).filter(BookingDB.id == booking_id).first()
    
    if booking_db is None:
        raise booking_exceptions.BookingNotFoundException(booking_id)
    
    booking = Booking.model_validate(booking_db)
    booking.total_cost = convert_booking_currency(booking.total_cost, booking.exchange_rate)
    return booking


def convert_booking_currency(total_cost_in_usd: Decimal, exchange_rate: Decimal) -> Decimal:
    return (total_cost_in_usd * exchange_rate).quantize(Decimal('0.00'))


def create_booking(booking: BookingCreate, user_id: int, db: Session) -> BookingDB:
     
    car = db.query(CarDB).filter(CarDB.id == booking.car_id).first()
    if not car:
        raise booking_exceptions.NoCarFoundException(booking.car_id)
    
    if not car.is_available:
        raise booking_exceptions.CarNotAvailableException(booking.car_id)
    
    if does_bookings_overlap(booking.car_id, booking.start_date, booking.end_date, db):
        raise booking_exceptions.BookingOverlapException(booking.car_id)
    
    total_cost = calculate_total_cost(car.price_per_day, booking.start_date, booking.end_date)
    
    # Exception will be raised if the currency converter service is unavailable
    currency_converter_client = get_currency_converter_client_instance()
    exchange_rate = currency_converter_client.get_currency_rate('USD', booking.currency_code.value)
    
    new_booking = BookingDB(
        user_id=user_id,
        car_id=booking.car_id,
        start_date=booking.start_date,
        end_date=booking.end_date,
        planned_pickup_time=booking.planned_pickup_time,  # Store time in UTC (without timezone)
        total_cost=total_cost,
        currency_code=booking.currency_code,
        exchange_rate=exchange_rate,
        status=BookingStatus.PLANNED
    )

    db.add(new_booking)
    db.commit()
    db.refresh(new_booking)

    return new_booking

def update_booking(booking_id: int, booking_update: BookingUpdate, db: Session):
    # Get and validate booking
    booking = db.query(BookingDB).filter(BookingDB.id == booking_id).first()
    if booking is None:
        raise booking_exceptions.BookingNotFoundException(booking_id)
    
    if booking.status in [BookingStatus.COMPLETED, BookingStatus.CANCELED]:
        raise booking_exceptions.BookingStateException(booking.status.value)
    
    # Process date updates
    update_data = booking_update.model_dump(exclude_unset=True)
    
    # Apply all validations
    handle_status_transitions(booking, update_data)
    
    start_date, end_date = get_updated_booking_period(booking, update_data)
    if not is_date_ordering_valid(start_date, end_date):
        raise booking_exceptions.DateRangeException()

    if does_bookings_overlap(booking.car_id, start_date, end_date, db, booking.id):
        raise booking_exceptions.BookingOverlapUpdateException()

    price_per_day = db.query(CarDB.price_per_day).filter(CarDB.id == booking.car_id).scalar()
    update_data['total_cost'] = calculate_total_cost(price_per_day, start_date, end_date)

    pickup_date, return_date = get_updated_usage_period(booking, update_data)
    if not is_date_ordering_valid(pickup_date, return_date):
        raise booking_exceptions.PickupAfterReturnException()

    handle_pickup_date_validations(booking, update_data)
    handle_return_date_validations(booking, update_data)
    
    # Update booking
    return apply_booking_updates(booking, update_data, db)

def does_bookings_overlap(car_id: int, start_date: date, end_date: date, db: Session, exclude_booking_id: int = None):
    """Check if the booking overlaps with existing bookings"""

    filters = [
        BookingDB.car_id == car_id,
        BookingDB.status.in_([BookingStatus.PLANNED, BookingStatus.ACTIVE]),
        BookingDB.start_date <= end_date,
        BookingDB.end_date >= start_date
    ]

    if exclude_booking_id:
        filters.append(BookingDB.id != exclude_booking_id)
    
    overlapping_bookings = db.query(BookingDB).filter(*filters).first()    
    return overlapping_bookings is not None

def calculate_booking_duration(start_date: date, end_date: date):
    """Calculate booking duration in days"""
    return (end_date - start_date).days + 1

def get_car_price_in_currency(car_price: Decimal, to_currency: str) -> Decimal:
    currency_converter_client = get_currency_converter_client_instance()
    return currency_converter_client.convert('USD', to_currency, car_price)

def calculate_total_cost(car_price: Decimal, start_date: date, end_date: date): 
    """Calculate total cost based on car price and booking duration"""   
    booking_duration = calculate_booking_duration(start_date, end_date)

    if booking_duration < 1:
        raise booking_exceptions.DateRangeException()

    return car_price * booking_duration   

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

def handle_status_transitions(booking: BookingDB, update_data: dict):
    """Handle status transitions with automatic date updates"""
    if 'status' not in update_data:
        return
        
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

def is_date_ordering_valid(start_date: date | None, end_date: date | None):
    if start_date is None or end_date is None:
        return True
    return start_date <= end_date

def handle_pickup_date_validations(booking: BookingDB, update_data: dict):
    """Handle all validations for pickup date"""
    if 'pickup_date' not in update_data:
        return
        
    if is_date_after_today(update_data['pickup_date']):
        raise booking_exceptions.FutureDateException("Pickup")
    
    # 2. Auto-update status when pickup_date is set
    if booking.status == BookingStatus.PLANNED:
        update_data['status'] = BookingStatus.ACTIVE
    
    # 3. Ensure pickup_date is within booking period
    start_date, end_date = get_updated_booking_period(booking, update_data)
    if not is_date_within_period(update_data['pickup_date'], start_date, end_date):
        raise booking_exceptions.DateOutsideBookingPeriodException("Pickup")

def handle_return_date_validations(booking: BookingDB, update_data: dict):
    """Handle all validations for return date"""
    if 'return_date' not in update_data:
        return
    
    # 1. Validate return_date can't be in the future
    if is_date_after_today(update_data['return_date']):
        raise booking_exceptions.FutureDateException("Return")
    
    # 2. Auto-update status when return_date is set
    current_status = update_data.get('status', booking.status)
    if (current_status == BookingStatus.ACTIVE or 
        booking.status == BookingStatus.ACTIVE or 
        booking.status == BookingStatus.OVERDUE):
        update_data['status'] = BookingStatus.COMPLETED
    
    # 3. Ensure return_date cannot be set if pickup_date is null
    if not booking.pickup_date and 'pickup_date' not in update_data:
        raise booking_exceptions.ReturnWithoutPickupException()
    
    # 4. Ensure return_date is within booking period (with OVERDUE exception)
    start_date, end_date = get_updated_booking_period(booking, update_data)
    allow_outside = booking.status == BookingStatus.OVERDUE
    if not is_date_within_period(update_data['return_date'], start_date, end_date, allow_outside):
        raise booking_exceptions.DateOutsideBookingPeriodException("Return")

def is_date_after_today(date_value):
    return date_value > date.today()

def get_updated_booking_period(booking, update_data):
    """Get the booking start and end dates, accounting for updates"""
    start_date = update_data.get('start_date', booking.start_date)
    end_date = update_data.get('end_date', booking.end_date)
    return start_date, end_date

def get_updated_usage_period(booking, update_data):
    """Get the booking start and end dates, accounting for updates"""
    start_date = update_data.get('pickup_date', booking.pickup_date)
    end_date = update_data.get('return_date', booking.return_date)
    return start_date, end_date
 
def is_date_within_period(date_value: date, start_date: date, end_date: date, allow_outside=False):
    """Validate that a date is within a period, with optional exception"""
    return date_value >= start_date and (date_value <= end_date or allow_outside)

def apply_booking_updates(booking: BookingDB, update_data: dict, db: Session):
    """Apply updates and save to the database"""
    for key, value in update_data.items():
        setattr(booking, key, value)
    
    db.commit()
    db.refresh(booking)
    return booking

def get_filtered_bookings(
    db: Session,
    pagination: PaginationParams,
    filters: Optional[BookingFilterParams] = None,
    user_id: Optional[int] = None,
    sort_params: Optional[SortParams] = None
) -> PaginatedResponse[Booking]:
    """
    Get bookings with filtering, sorting, and pagination.
    
    Args:
        db: Database session
        pagination: Pagination parameters
        filters: Optional filter parameters
        user_id: Optional user ID to filter by (for "my bookings")
        sort_params: Optional sorting parameters
        
    Returns:
        PaginatedResponse containing bookings and pagination metadata
    """
    # Start with base query
    query = db.query(BookingDB)
    
    # Apply user filter if provided (for "my bookings")
    if user_id is not None:
        query = query.filter(BookingDB.user_id == user_id)
    
    # Apply filters if provided
    if filters:
        if filters.status:
            try:
                # Try to match with BookingStatus enum
                status = BookingStatus(filters.status)
                query = query.filter(BookingDB.status == status)
            except ValueError:
                # If not a valid enum value, filter will return empty result
                pass
                
        if filters.car_id:
            query = query.filter(BookingDB.car_id == filters.car_id)
            
        if filters.start_date_from:
            query = query.filter(BookingDB.start_date >= filters.start_date_from)
            
        if filters.start_date_to:
            query = query.filter(BookingDB.start_date <= filters.start_date_to)
            
        if filters.end_date_from:
            query = query.filter(BookingDB.end_date >= filters.end_date_from)
            
        if filters.end_date_to:
            query = query.filter(BookingDB.end_date <= filters.end_date_to)
    
    # Apply sorting if provided
    if sort_params:
        # Check if the attribute exists on the BookingDB model
        if hasattr(BookingDB, sort_params.sort_by):
            sort_column = getattr(BookingDB, sort_params.sort_by)
            
            if sort_params.sort_order == "desc":
                sort_column = desc(sort_column)
                
            query = query.order_by(sort_column)
        else:
            # Default to sorting by ID if column doesn't exist
            query = query.order_by(BookingDB.id)
    else:
        # Default sort by ID
        query = query.order_by(BookingDB.id)
    
    # Count total items for pagination metadata
    total_items = query.count()
    
    # Calculate total pages
    total_pages = (total_items + pagination.page_size - 1) // pagination.page_size if total_items > 0 else 0
    
    # Apply pagination
    offset = (pagination.page - 1) * pagination.page_size
    query = query.offset(offset).limit(pagination.page_size)
    
    # Execute query
    bookings_db = query.all()
    
    # Convert to Pydantic models
    bookings = []
    for booking_db in bookings_db:
        booking = Booking.model_validate(booking_db)
        booking.total_cost = convert_booking_currency(booking.total_cost, booking.exchange_rate)
        bookings.append(booking)
    
    # Return paginated response
    return PaginatedResponse[Booking](
        items=bookings,
        total=total_items,
        page=pagination.page,
        page_size=pagination.page_size,
        pages=total_pages
    )