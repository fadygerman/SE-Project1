from datetime import date, time
from decimal import Decimal

from fastapi import Depends, HTTPException
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from database import get_db
from main import app
from models.currencies import Currency
from models.db_models import Base, Booking, BookingStatus, Car, User, UserRole
from services.auth_service import get_current_user, require_role

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

# Create test data
@pytest.fixture
def test_data(test_db):
    # Create test users
    user1 = User(
        first_name="Test",
        last_name="User1",
        email="testuser1@example.com",
        phone_number="+1234567890",
        cognito_id="cognito1"
    )
    
    user2 = User(
        first_name="Test",
        last_name="User2",
        email="testuser2@example.com",
        phone_number="+0987654321",
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
        planned_pickup_time=time(10, 30),
        pickup_date=None,
        return_date=None,
        total_cost=Decimal("200.00"),
        exchange_rate=Decimal("1.00"),
        currency_code=Currency.USD,
        status=BookingStatus.PLANNED
    )
    
    booking2 = Booking(
        user_id=user2.id,
        car_id=car2.id,
        start_date=date(2024, 5, 1),
        end_date=date(2024, 5, 3),
        planned_pickup_time=time(14, 0),
        pickup_date=date(2024, 5, 1),
        return_date=None,
        total_cost=Decimal("150.00"),
        exchange_rate=Decimal("0.88"),
        currency_code=Currency.EUR,
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

# Override the dependency for testing
@pytest.fixture
def client(test_db):
    # Override the get_db dependency
    def override_get_db():
        try:
            yield test_db
        finally:
            pass
    
    # Store the original dependency overrides
    original_overrides = app.dependency_overrides.copy()
    
    # Set up dependency overrides
    app.dependency_overrides[get_db] = override_get_db
    
    # Create the test client
    with TestClient(app) as c:
        yield c
    
    # Restore original dependency overrides
    app.dependency_overrides = original_overrides

# Fixtures for authenticated clients
@pytest.fixture
def auth_client(client, test_data):
    """Client with regular user authentication"""
    # Create an async function that returns a test user
    async def override_get_current_user():
        return test_data["users"][0]
        
    # Store the original dependency overrides
    original_overrides = app.dependency_overrides.copy()
    
    # Override the auth dependency
    app.dependency_overrides[get_current_user] = override_get_current_user
    
    yield client
    
    # Restore original dependency overrides
    app.dependency_overrides = original_overrides

@pytest.fixture
def admin_client(client, test_data):
    """Client with admin authentication"""
    # Create an async function that returns a test user with admin role
    async def override_get_current_user():
        # Return the first user but assign the admin role
        user = test_data["users"][0]
        user.role = UserRole.ADMIN  # Assign the admin role directly
        return user

    # Store the original dependency overrides
    original_overrides = app.dependency_overrides.copy()

    # Override only the get_current_user dependency
    app.dependency_overrides[get_current_user] = override_get_current_user

    # Yield the client for the test
    yield client

    # Restore original dependency overrides after the test
    app.dependency_overrides = original_overrides
