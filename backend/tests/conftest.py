import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient
from decimal import Decimal
from datetime import date

from main import app
from database import get_db
from models.db_models import User, Car, Booking, BookingStatus, Base

# Create test database
SQLALCHEMY_TEST_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_TEST_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Override the get_db dependency
@pytest.fixture
def test_db():
    # Create the test database and tables
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    
    try:
        yield db
    finally:
        db.close()
        # Clean up after test
        Base.metadata.drop_all(bind=engine)

# Override the dependency
@pytest.fixture
def client(test_db):
    def override_get_db():
        try:
            yield test_db
        finally:
            pass
    
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()

# Add test data
@pytest.fixture
def test_data(test_db):
    # Create test users
    user1 = User(
        first_name="Test",
        last_name="User1",
        email="testuser1@example.com",
        phone_number="+1234567890",
        password_hash="hash1",
        cognito_id="cognito1"
    )
    
    user2 = User(
        first_name="Test",
        last_name="User2",
        email="testuser2@example.com",
        phone_number="+0987654321",
        password_hash="hash2",
        cognito_id="cognito2"
    )
    
    # Create test cars
    car1 = Car(
        name="TestCar1",
        model="Model1",
        price_per_day=Decimal("50.00"),
        is_available=True,
        latitude=40.7128,
        longitude=-74.0060
    )
    
    car2 = Car(
        name="TestCar2",
        model="Model2",
        price_per_day=Decimal("75.00"),
        is_available=False,
        latitude=34.0522,
        longitude=-118.2437
    )
    
    # Add users and cars to the database
    test_db.add_all([user1, user2, car1, car2])
    test_db.commit()
    
    # Refresh to get IDs assigned
    test_db.refresh(user1)
    test_db.refresh(user2)
    test_db.refresh(car1)
    test_db.refresh(car2)
    
    # Create test bookings
    booking1 = Booking(
        user_id=user1.id,
        car_id=car1.id,
        start_date=date(2024, 4, 1),
        end_date=date(2024, 4, 5),
        pickup_date=None,
        return_date=None,
        total_cost=Decimal("200.00"),
        status=BookingStatus.PLANNED
    )
    
    booking2 = Booking(
        user_id=user2.id,
        car_id=car2.id,
        start_date=date(2024, 5, 1),
        end_date=date(2024, 5, 3),
        pickup_date=date(2024, 5, 1),
        return_date=None,
        total_cost=Decimal("150.00"),
        status=BookingStatus.ACTIVE
    )
    
    # Add bookings to the database
    test_db.add_all([booking1, booking2])
    test_db.commit()
    
    # Refresh to get IDs assigned
    test_db.refresh(booking1)
    test_db.refresh(booking2)
    
    # Return test data for use in tests
    return {
        "users": [user1, user2],
        "cars": [car1, car2],
        "bookings": [booking1, booking2]
    }