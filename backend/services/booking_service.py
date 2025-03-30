import exceptions.bookings as booking_exceptions
from models.db_models import Booking as BookingModel, Car as CarModel, BookingStatus
from models.models import BookingCreate
from sqlalchemy.orm import Session


def create_booking(booking: BookingCreate, db: Session):
  car = db.query(CarModel).filter(CarModel.id == booking.car_id).first()
  if not car:
    raise booking_exceptions.NoCarFoundException(booking.car_id)
  
  if not car.is_available:
    raise booking_exceptions.CarNotAvailableException(booking.car_id)
  
  if does_bookings_overlap(booking, db):
    raise booking_exceptions.BookingOverlapException(booking.car_id)
  
  booking_duration = calculate_booking_duration(booking)
  if booking_duration < 1:
    raise booking_exceptions.BookingTooShortException(booking.car_id)
  
  total_cost = calculate_total_cost(car, booking_duration)
  
  new_booking = BookingModel(
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


def does_bookings_overlap(booking: BookingCreate, db: Session):
  overlapping_bookings = db.query(BookingModel).filter(
        BookingModel.car_id == booking.car_id,
        BookingModel.status.in_([BookingStatus.PLANNED, BookingStatus.ACTIVE]),
        BookingModel.start_date <= booking.end_date,
        BookingModel.end_date >= booking.start_date
  ).first()
  
  return overlapping_bookings is not None

def calculate_booking_duration(booking: BookingCreate):
  return (booking.end_date - booking.start_date).days + 1

def calculate_total_cost(car: CarModel, booking_duration: int):
  return car.price_per_day * booking_duration
  