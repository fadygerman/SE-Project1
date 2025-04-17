from datetime import date
from decimal import Decimal

from sqlalchemy.orm import Session

import exceptions.bookings as booking_exceptions
from currency_converter.client import get_currency_converter_client_instance
from models.db_models import Booking as BookingDB
from models.db_models import BookingStatus
from models.db_models import Car as CarDB
from models.pydantic.booking import BookingCreate, BookingUpdate


def create_booking(booking: BookingCreate, user_id: int, db: Session):
    """Creates a new booking in the database.

    Validates car availability and checks for overlapping bookings before
    creating the new booking record. Calculates the total cost based on
    car price and duration, and fetches the currency exchange rate.

    Args:
        booking_data: The Pydantic model containing the booking creation details
                      (car_id, start_date, end_date, planned_pickup_time, currency_code).
        user_id: The ID of the user creating the booking.
        db: The database session dependency.

    Returns:
        The newly created BookingDB object.
    """   
    car = db.query(CarDB).filter(CarDB.id == booking.car_id).first()
    if not car:
        raise booking_exceptions.NoCarFoundException(booking.car_id)
    
    if not car.is_available:
        raise booking_exceptions.CarNotAvailableException(booking.car_id)
    
    if does_bookings_overlap(booking.car_id, booking.start_date, booking.end_date, db):
        raise booking_exceptions.BookingOverlapException(booking.car_id)
    
    total_cost = calculate_total_cost(car.price_per_day, booking.start_date, booking.end_date)
    
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