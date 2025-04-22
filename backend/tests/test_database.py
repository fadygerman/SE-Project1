import os
from datetime import date, time
from decimal import Decimal

from sqlalchemy import create_engine, select, text
from sqlalchemy.orm import sessionmaker

from db_seed import init_db, seed_data
from models.db_models import Base, Booking, BookingStatus, Car, User


def test_postgres_connection(postgres_container):
    """Test that we can connect to the PostgreSQL database container"""
    # The postgres_container fixture provides a database URL string
    
    # Create a new engine using the container connection string
    test_engine = create_engine(postgres_container)
    
    # Test the connection by executing a simple query
    with test_engine.connect() as connection:
        result = connection.execute(text("SELECT 1"))
        assert result.scalar() == 1
        
    assert os.environ["DB_HOST"] is not None
    assert os.environ["DB_PORT"] is not None


def test_seed_and_query(test_db, test_data):
    """Test seeding the database using db_seed.py and verifying the data"""
    
    # Verify cars were inserted
    stmt = select(Car)
    cars = test_db.scalars(stmt).all()
    assert len(cars) >= 2  # At least 4 cars should be inserted
    
    # Verify some cars in seed data
    car_models = [(car.name, car.model) for car in cars]
    assert ("TestCar1", "Model1") in car_models
    assert ("TestCar2", "Model2") in car_models
    
    # Verify bookings were inserted
    stmt = select(Booking)
    bookings = test_db.scalars(stmt).all()
    assert len(bookings) >= 2  # At least 2 bookings should be inserted