'''
This script initializes the database and seeds it with sample data.
This is only for development purposes and should not be used in production environments

To run this script, execute the following command in the terminal:
> python db_seed.py
'''

from datetime import date, time, timedelta
from decimal import Decimal

import dotenv

dotenv.load_dotenv()

from database import SessionLocal, engine
from models.currencies import Currency
from models.db_models import Base, Booking, BookingStatus, Car, User, UserRole


# Create all tables in the database
def init_db():
    Base.metadata.drop_all(bind=engine)
    print("Existing tables dropped!")
    Base.metadata.create_all(bind=engine)
    print("Database created!")

# Seed the database with sample data
def seed_data():
    db = SessionLocal()
    
    # First, clear any existing data
    db.query(Booking).delete()
    db.query(Car).delete()
    db.query(User).delete()
    
    # Create sample users with different roles
    users = [
        User(
            first_name="John", 
            last_name="Doe", 
            email="john.doe@example.com", 
            phone_number="+14155552671", 
            cognito_id="cognito_sample_id_1",
            role=UserRole.USER  # Regular user
        ),
        User(
            first_name="Jane", 
            last_name="Smith", 
            email="jane.smith@example.com", 
            phone_number="+14155552672", 
            cognito_id="cognito_sample_id_2",
            role=UserRole.ADMIN  # Admin user
        ),
        User(
            first_name="Robert", 
            last_name="Johnson", 
            email="robert.johnson@example.com", 
            phone_number="+14155552673", 
            cognito_id="cognito_sample_id_3",
            role=UserRole.USER
        ),
        User(
            first_name="Emily", 
            last_name="Wilson", 
            email="emily.wilson@example.com", 
            phone_number="+14155552674", 
            cognito_id="cognito_sample_id_4",
            role=UserRole.USER  # Another regular user
        )
    ]
    
    for user in users:
        db.add(user)
    
    # Create sample cars with various properties
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
            is_available=False,  # Currently unavailable
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
            is_available=False,  # Currently unavailable
            latitude=37.7749,
            longitude=-122.4194
        ),
        Car(
            name="BMW",
            model="X5",
            price_per_day=Decimal("120.0"),
            is_available=True,
            latitude=48.8566,
            longitude=2.3522
        ),
        Car(
            name="Mercedes",
            model="E-Class",
            price_per_day=Decimal("110.0"),
            is_available=True,
            latitude=52.5200,
            longitude=13.4050
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
    
    # Get today's date for relative booking dates
    today = date.today()
    
    # Create sample bookings with various statuses
    bookings = [
        # Planned booking (in the future)
        Booking(
            user_id=users[0].id,  # John Doe (regular user)
            car_id=cars[2].id,    # Ford Mustang
            start_date=today + timedelta(days=15),
            end_date=today + timedelta(days=20),
            pickup_date=None,     # Not picked up yet
            return_date=None,     # Not returned yet
            planned_pickup_time=time(10, 30),  # 10:30 AM (UTC)
            total_cost=Decimal("375.0"),
            currency_code=Currency.USD,
            exchange_rate=Decimal("1.00"),
            status=BookingStatus.PLANNED
        ),
        # Completed booking (in the past)
        Booking(
            user_id=users[1].id,  # Jane Smith (admin)
            car_id=cars[0].id,    # Toyota Corolla
            start_date=today - timedelta(days=20),
            end_date=today - timedelta(days=15),
            pickup_date=today - timedelta(days=20),
            return_date=today - timedelta(days=15),
            planned_pickup_time=time(14, 0),  # 2:00 PM (UTC)
            total_cost=Decimal("225.0"),
            currency_code=Currency.USD,
            exchange_rate=Decimal("1.00"),
            status=BookingStatus.COMPLETED
        ),
        # Active booking (currently ongoing)
        Booking(
            user_id=users[3].id,  # Emily Wilson (regular user)
            car_id=cars[3].id,    # Chevrolet Camaro
            start_date=today - timedelta(days=2),
            end_date=today + timedelta(days=3),
            pickup_date=today - timedelta(days=2),
            return_date=None,     # Not returned yet
            planned_pickup_time=time(9, 0),   # 9:00 AM (UTC)
            total_cost=Decimal("350.0"),
            currency_code=Currency.USD,
            exchange_rate=Decimal("1.00"),
            status=BookingStatus.ACTIVE
        ),
        # Canceled booking
        Booking(
            user_id=users[2].id,  # Robert Johnson (regular user)
            car_id=cars[5].id,    # BMW X5
            start_date=today + timedelta(days=5),
            end_date=today + timedelta(days=10),
            pickup_date=None,
            return_date=None,
            planned_pickup_time=time(16, 30),  # 4:30 PM (UTC)
            total_cost=Decimal("600.0"),
            currency_code=Currency.USD,
            exchange_rate=Decimal("1.00"),
            status=BookingStatus.CANCELED
        ),
        # Overdue booking (not returned on time)
        Booking(
            user_id=users[0].id,  # John Doe (regular user)
            car_id=cars[6].id,    # Mercedes E-Class
            start_date=today - timedelta(days=10),
            end_date=today - timedelta(days=5),
            pickup_date=today - timedelta(days=10),
            return_date=None,     # Not returned yet, but should have been
            planned_pickup_time=time(11, 0),  # 11:00 AM (UTC)
            total_cost=Decimal("550.0"),
            currency_code=Currency.USD,
            exchange_rate=Decimal("1.00"),
            status=BookingStatus.OVERDUE
        ),
        # Another planned booking with EUR currency
        Booking(
            user_id=users[3].id,  # Emily Wilson (regular user)
            car_id=cars[1].id,    # Honda Civic
            start_date=today + timedelta(days=30),
            end_date=today + timedelta(days=35),
            pickup_date=None,
            return_date=None,
            planned_pickup_time=time(13, 15),  # 1:15 PM (UTC)
            total_cost=Decimal("250.0"),
            currency_code=Currency.EUR,
            exchange_rate=Decimal("0.85"),
            status=BookingStatus.PLANNED
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