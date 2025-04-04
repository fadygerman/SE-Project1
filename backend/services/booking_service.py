from decimal import Decimal
import exceptions.bookings as booking_exceptions
from models.db_models import Booking as BookingDB, Car as CarDB, BookingStatus
from models.models import BookingCreate, BookingUpdate
from sqlalchemy.orm import Session
from datetime import date
from contextlib import contextmanager

def create_booking(booking: BookingCreate, db: Session):
  car = db.query(CarDB).filter(CarDB.id == booking.car_id).first()
  if not car:
    raise booking_exceptions.NoCarFoundException(booking.car_id)
  
  if not car.is_available:
    raise booking_exceptions.CarNotAvailableException(booking.car_id)
  
  if does_bookings_overlap(booking, db):
    raise booking_exceptions.BookingOverlapException(booking.car_id)
  
  total_cost = calculate_total_cost(car.price_per_day, booking.start_date, booking.end_date)
  
  new_booking = BookingDB(
      user_id=booking.user_id,
      car_id=booking.car_id,
      start_date=booking.start_date,
      end_date=booking.end_date,
      total_cost=total_cost,
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
    
    if validate_date_ordering(booking, update_data, 'start_date', 'end_date'):
        raise booking_exceptions.DateRangeException()

    if does_bookings_overlap(booking, db, update_data):
        raise booking_exceptions.BookingOverlapUpdateException()

    price_per_day = db.query(CarDB.price_per_day).filter(CarDB.id == booking.car_id).scalar()
    start_date, end_date = get_booking_period(booking, update_data)
    update_data['total_cost'] = calculate_total_cost(price_per_day, start_date, end_date)


    if validate_date_ordering(booking, update_data, 'pickup_date', 'return_date'):
        raise booking_exceptions.PickupAfterReturnException()

    handle_pickup_date_validations(booking, update_data)
    handle_return_date_validations(booking, update_data)
    
    # Update booking
    return apply_booking_updates(booking, update_data, db)

def does_bookings_overlap(booking, db: Session, update_data=None):
    with temporary_date_update(booking, update_data):
        filters = [
            BookingDB.car_id == booking.car_id,
            BookingDB.status.in_([BookingStatus.PLANNED, BookingStatus.ACTIVE]),
            BookingDB.start_date <= booking.end_date,
            BookingDB.end_date >= booking.start_date
        ]
    
        if hasattr(booking, 'id'):
            filters.append(BookingDB.id != booking.id)
        
        overlapping_bookings = db.query(BookingDB).filter(*filters).first()    
        return overlapping_bookings is not None

def calculate_booking_duration(start_date: date, end_date: date):
    """Calculate booking duration in days"""
    return (end_date - start_date).days + 1
  
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

def validate_date_ordering(booking: BookingDB, update_data: dict, first_field: str, second_field: str):
    """ Generic date validation function that ensures one date comes before another. """
    # Case 1: Both dates are being updated
    if first_field in update_data and second_field in update_data:
        return update_data[second_field] < update_data[first_field]
    
    # Case 2: Only second date is updated, check against existing first date
    elif second_field in update_data and getattr(booking, first_field, None):
        return update_data[second_field] < getattr(booking, first_field)
    
    # Case 3: Only first date is updated, check against existing second date
    elif first_field in update_data and getattr(booking, second_field, None):
        return getattr(booking, second_field) < update_data[first_field]
    
    return False

def handle_pickup_date_validations(booking: BookingDB, update_data: dict):
    """Handle all validations for pickup date"""
    if 'pickup_date' not in update_data:
        return
        
    # 1. Validate pickup_date can't be in the future
    validate_date_not_in_future(update_data['pickup_date'], "Pickup")
    
    # 2. Auto-update status when pickup_date is set
    if booking.status == BookingStatus.PLANNED:
        update_data['status'] = BookingStatus.ACTIVE
    
    # 3. Ensure pickup_date is within booking period
    start_date, end_date = get_booking_period(booking, update_data)
    validate_date_within_period(update_data['pickup_date'], start_date, end_date, "Pickup")

def handle_return_date_validations(booking: BookingDB, update_data: dict):
    """Handle all validations for return date"""
    if 'return_date' not in update_data:
        return
    
    # 1. Validate return_date can't be in the future
    validate_date_not_in_future(update_data['return_date'], "Return")
    
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
    start_date, end_date = get_booking_period(booking, update_data)
    allow_outside = booking.status == BookingStatus.OVERDUE
    validate_date_within_period(update_data['return_date'], start_date, end_date, "Return", allow_outside)

def validate_date_not_in_future(date_value, date_type):
    """Validate that a date is not in the future"""
    if date_value > date.today():
        raise booking_exceptions.FutureDateException(date_type)

def get_booking_period(booking, update_data):
    """Get the booking start and end dates, accounting for updates"""
    start_date = update_data.get('start_date', booking.start_date)
    end_date = update_data.get('end_date', booking.end_date)
    return start_date, end_date

def validate_date_within_period(date_value, start_date, end_date, date_type, allow_outside=False):
    """Validate that a date is within a period, with optional exception"""
    if date_value < start_date or (date_value > end_date and not allow_outside):
        raise booking_exceptions.DateOutsideBookingPeriodException(date_type)

def apply_booking_updates(booking: BookingDB, update_data: dict, db: Session):
    """Apply updates and save to the database"""
    for key, value in update_data.items():
        setattr(booking, key, value)
    
    db.commit()
    db.refresh(booking)
    return booking

@contextmanager
def temporary_date_update(booking, update_data):
    """Temporarily update booking dates for operations that need them"""
    if not update_data or ('start_date' not in update_data and 'end_date' not in update_data):
        yield
        return
        
    original_start, original_end = booking.start_date, booking.end_date
    try:
        booking.start_date, booking.end_date = get_booking_period(booking, update_data)
        yield
    finally:
        booking.start_date, booking.end_date = original_start, original_end
