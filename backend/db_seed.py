'''
This script initializes the database and seeds it with sample data.
This is only for development purposes and should not be used in production environments

To run this script, execute the following command in the terminal:
> python db_seed.py
'''


from datetime import date
from decimal import Decimal
import enum

from sqlalchemy.orm import Session
from database import SessionLocal, engine, Base
from models.db_models import User, Car, Booking, BookingStatus

# Create all tables in the database
def init_db():
    Base.metadata.create_all(bind=engine)
    print("Database created!")

# Seed the database with sample data
def seed_data():
    db = SessionLocal()
    
    # First, clear any existing data
    db.query(Booking).delete()
    db.query(Car).delete()
    db.query(User).delete()
    
    # Create sample users
    users = [
        User(
            first_name="John", 
            last_name="Doe", 
            email="john.doe@example.com", 
            phone_number="+14155552671", 
            password_hash="$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW"  # "password"
        ),
        User(
            first_name="Jane", 
            last_name="Smith", 
            email="jane.smith@example.com", 
            phone_number="+14155552672", 
            password_hash="$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW"
        )
    ]
    
    for user in users:
        db.add(user)
    
    # Create sample cars
    cars = [
        Car(
            name="Toyota",
            model="Corolla",
            price_per_day=Decimal("45.0"),
            is_available=True,
            latitude=35.6895,
            longitude=139.6917
        ),
        Car(
            name="Honda",
            model="Civic",
            price_per_day=Decimal("50.0"),
            is_available=False,
            latitude=34.0522,
            longitude=-118.2437
        ),
        Car(
            name="Ford",
            model="Mustang",
            price_per_day=Decimal("75.0"),
            is_available=True,
            latitude=51.5074,
            longitude=-0.1278
        ),
        Car(
            name="Chevrolet",
            model="Camaro",
            price_per_day=Decimal("70.0"),
            is_available=True,
            latitude=40.7128,
            longitude=-74.0060
        ),
        Car(
            name="Tesla",
            model="Model 3",
            price_per_day=Decimal("100.0"),
            is_available=False,
            latitude=37.7749,
            longitude=-122.4194
        )
    ]
    
    for car in cars:
        db.add(car)
    
    # Commit to save users and cars
    db.commit()
    
    # Refresh to get the ids
    for user in users:
        db.refresh(user)
    for car in cars:
        db.refresh(car)
    
    # Create sample bookings
    bookings = [
        Booking(
            user_id=users[0].id,
            car_id=cars[2].id,
            start_date=date(2025, 4, 1),
            end_date=date(2025, 4, 5),
            pickup_date=None,  # Will be set when user picks up the car
            return_date=None,  # Will be set when user returns the car
            total_cost=Decimal("375.0"),
            status=BookingStatus.PLANNED
        ),
        Booking(
            user_id=users[1].id,
            car_id=cars[0].id,
            start_date=date(2025, 3, 15),
            end_date=date(2025, 3, 20),
            pickup_date=date(2025, 3, 15),
            return_date=date(2025, 3, 20),
            total_cost=Decimal("225.0"),
            status=BookingStatus.COMPLETED
        )
    ]
    
    for booking in bookings:
        db.add(booking)
    
    # Commit all changes
    db.commit()
    print("Sample data added!")
    db.close()

if __name__ == "__main__":
    init_db()
    seed_data()