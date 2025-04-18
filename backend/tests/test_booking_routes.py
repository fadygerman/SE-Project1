from datetime import date, timedelta
from decimal import Decimal
from unittest import mock
from unittest.mock import Mock, patch

import pytest
from fastapi import status

from exceptions.currencies import CurrencyServiceUnavailableException
from main import app
from models.db_models import Booking, BookingStatus
from services.booking_service import get_car_price_in_currency


class TestBookingCreation:
    """Tests related to creating bookings"""
    
    @patch('models.pydantic.booking.date')
    def test_create_valid_booking(self, mock_date, auth_client, test_data):
        """Test successfully creating a booking
        ATTENTION: Currency converter must be running to pass this test
        """
        # Mock today's date
        mock_today = date(2024, 3, 15)
        mock_date.today.return_value = mock_today
        # Ensure date class still works otherwise
        mock_date.side_effect = lambda *args, **kw: date(*args, **kw)
        
        user_id = test_data["users"][0].id
        car_id = test_data["cars"][0].id
        
        # Create a booking with start date at least tomorrow
        tomorrow = mock_today + timedelta(days=1)
        start_date = tomorrow
        end_date = start_date + timedelta(days=3)
        
        booking_data = {
            # No need to specify user_id as it will be taken from the authenticated user
            "car_id": car_id,
            "start_date": str(start_date),
            "end_date": str(end_date),
            "planned_pickup_time": "10:00:00",
            "currency_code": "EUR",
        }
        
        response = auth_client.post("/api/v1/bookings/", json=booking_data)
        
        # Check status code
        assert response.status_code == status.HTTP_201_CREATED
        
        # Check response data
        created_booking = response.json()
        assert created_booking["user_id"] == user_id  # Should use auth user's ID
        assert created_booking["car_id"] == car_id
        assert created_booking["start_date"] == str(start_date)
        assert created_booking["end_date"] == str(end_date)
        assert created_booking["status"] == "PLANNED"
        assert created_booking["currency_code"] == "EUR"
        assert created_booking["exchange_rate"] is not None
        
        # Check total cost calculation (4 days × car price)
        car_price = float(test_data["cars"][0].price_per_day)
        expected_total = car_price * 4
        assert float(created_booking["total_cost"]) == expected_total

    @patch('services.booking_service.get_currency_converter_client_instance')
    def test_create_booking_currency_service_unavailable(self, mock_currency_converter_client, auth_client, test_data):
        """Test creating a booking when currency service is unavailable"""
        # Mock the currency converter client to raise an exception
        mock_currency_converter_client.side_effect = CurrencyServiceUnavailableException("Currency service unavailable")
        
        booking_data = {
            "user_id": test_data["users"][0].id,
            "car_id": test_data["cars"][0].id,
            "start_date": "2025-06-01",
            "end_date": "2025-06-05",
            "planned_pickup_time": "09:30:00",
            "currency_code": "EUR",  # Using non-USD currency to trigger conversion
        }
        
        response = auth_client.post("/api/v1/bookings/", json=booking_data)
        
        # Check status code - should be service unavailable
        assert response.status_code == status.HTTP_503_SERVICE_UNAVAILABLE
        
        # Check error message
        error = response.json()
        assert "Currency service is unavailable" in error["detail"]

    def test_create_booking_car_not_found(self, auth_client, test_data):
        """Test creating a booking with non-existent car ID"""
        booking_data = {
            "user_id": test_data["users"][0].id,
            "car_id": 999,  # Non-existent car ID
            "start_date": "2025-06-01",
            "end_date": "2025-06-05",
            "planned_pickup_time": "09:30:00",
            "currency_code": "USD",
        }
        
        response = auth_client.post("/api/v1/bookings/", json=booking_data)
        
        # Check status code
        assert response.status_code == status.HTTP_404_NOT_FOUND
        
        # Check error message
        error = response.json()
        assert "Car with ID 999 not found" in error["detail"]

    def test_create_booking_unavailable_car(self, auth_client, test_data):
        """Test creating a booking for an unavailable car"""
        # Car 2 is marked as unavailable in test data
        unavailable_car_id = test_data["cars"][1].id
        
        booking_data = {
            "user_id": test_data["users"][0].id,
            "car_id": unavailable_car_id,
            "start_date": "2025-06-01",
            "end_date": "2025-06-05",
            "planned_pickup_time": "14:00:00",
            "currency_code": "USD",
        }
        
        response = auth_client.post("/api/v1/bookings/", json=booking_data)
        
        # Check status code
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        
        # Check error message
        error = response.json()
        assert f"Car with ID {unavailable_car_id} is not available" in error["detail"]

    @patch('models.pydantic.booking.date')
    def test_create_booking_start_date_today(self, mock_date, auth_client, test_data):
        # Setup mock for date.today()
        mock_today = date(2024, 5, 15)
        mock_date.today.return_value = mock_today
        # Ensure date class still works otherwise
        mock_date.side_effect = lambda *args, **kw: date(*args, **kw)
        
        booking_data = {
            "user_id": test_data["users"][0].id,
            "car_id": test_data["cars"][0].id,
            "start_date": str(mock_today),     # Today's date
            "end_date": str(mock_today + timedelta(days=5)),
            "planned_pickup_time": "12:00:00",
            "currency_code": "USD",
        }
        
        response = auth_client.post("/api/v1/bookings/", json=booking_data)
        
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        
        error = response.json()
        assert "Start date must be tomorrow or later" in str(error)
    
    @patch('models.pydantic.booking.date')
    def test_create_booking_start_date_past(self, mock_date, auth_client, test_data):
        # Setup mock for date.today()
        mock_today = date(2024, 5, 15)
        mock_date.today.return_value = mock_today
        # Ensure date class still works otherwise
        mock_date.side_effect = lambda *args, **kw: date(*args, **kw)
        
        past_date = mock_today - timedelta(days=3)
        booking_data = {
            "user_id": test_data["users"][0].id,
            "car_id": test_data["cars"][0].id,
            "start_date": str(past_date),     # Date in the past
            "end_date": str(mock_today + timedelta(days=5)),
            "planned_pickup_time": "11:30:00",
            "currency_code": "USD",
        }
        
        response = auth_client.post("/api/v1/bookings/", json=booking_data)
        
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        
        error = response.json()
        assert "Start date must be tomorrow or later" in str(error)

    @patch('models.pydantic.booking.date')
    def test_create_booking_overlapping_dates(self, mock_date, auth_client, test_data):
        """Test creating a booking with dates that overlap with existing booking"""        
        # Setup mock for date.today()
        mock_today = date(2024, 3, 29)
        mock_date.today.return_value = mock_today
        mock_date.side_effect = lambda *args, **kw: date(*args, **kw)
        
        # Get existing booking dates
        existing_booking = test_data["bookings"][0]
        
        # Try to book the same car with overlapping dates
        booking_data = {
            "user_id": test_data["users"][0].id,
            "car_id": existing_booking.car_id,
            "start_date": str(existing_booking.start_date),  # Same start date
            "end_date": str(existing_booking.end_date + timedelta(days=5)),  # Extended end date
            "planned_pickup_time": "10:30:00",
            "currency_code": "USD",
        }
        
        response = auth_client.post("/api/v1/bookings/", json=booking_data)
        
        # Check status code
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        
        # Check error message
        error = response.json()
        assert "already booked for the selected dates" in error["detail"]

    def test_create_booking_invalid_dates(self, auth_client, test_data):
        """Test creating a booking with end date before start date"""
        booking_data = {
            "user_id": test_data["users"][0].id,
            "car_id": test_data["cars"][0].id,
            "start_date": "2025-06-05",  # Later date
            "end_date": "2025-06-01",     # Earlier date
            "planned_pickup_time": "10:30:00",
            "currency_code": "USD",
        }
        
        response = auth_client.post("/api/v1/bookings/", json=booking_data)
        
        # Check status code and error
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        
        # Pydantic validation should catch this
        error = response.json()
        assert "End date must be after start date" in str(error)

    @patch('models.pydantic.booking.date')
    def test_create_booking_without_end_date(self, mock_date, auth_client, test_data):
        """Test creating a booking without providing an end_date"""
        # Setup mock for date.today()
        mock_today = date(2024, 5, 15)
        mock_date.today.return_value = mock_today
        mock_date.side_effect = lambda *args, **kw: date(*args, **kw)
        
        # Create a booking data without end_date
        booking_data = {
            "user_id": test_data["users"][0].id,
            "car_id": test_data["cars"][0].id,
            "start_date": str(mock_today + timedelta(days=5)),  # Valid future date
            "planned_pickup_time": "10:30:00",
            # No end_date provided
            "currency_code": "USD",
        }
        
        response = auth_client.post("/api/v1/bookings/", json=booking_data)
        
        # Check status code - should be validation error
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        
        # Check error message
        error = response.json()
        assert "end_date" in str(error)  # Field should be mentioned in the error
        assert "field required" in str(error).lower()  # Standard Pydantic missing field message

    def test_create_booking_without_planned_pickup_time(self, auth_client, test_data):
        """Test creating a booking without providing a planned pickup time"""
        # Create booking data without planned_pickup_time
        booking_data = {
            "user_id": test_data["users"][0].id,
            "car_id": test_data["cars"][0].id,
            "start_date": str(date.today() + timedelta(days=5)),  # Valid future date
            "end_date": str(date.today() + timedelta(days=10)),
            # No planned_pickup_time provided
            "currency_code": "USD",
        }
        
        response = auth_client.post("/api/v1/bookings/", json=booking_data)
        
        # Check status code - should be validation error
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        
        # Check error message
        error = response.json()
        assert "planned_pickup_time" in str(error)  # Field should be mentioned in the error
        assert "field required" in str(error).lower()  # Standard Pydantic missing field message

    def test_create_booking_with_invalid_pickup_time_format(self, auth_client, test_data):
        """Test creating a booking with an invalid planned_pickup_time format"""
        booking_data = {
            "user_id": test_data["users"][0].id,
            "car_id": test_data["cars"][0].id,
            "start_date": str(date.today() + timedelta(days=5)),
            "end_date": str(date.today() + timedelta(days=10)),
            "planned_pickup_time": "10:30 AM"  # Invalid format (should be HH:MM:SS)
        }
        
        response = auth_client.post("/api/v1/bookings/", json=booking_data)
        
        # Check status code - should be validation error
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        
        # Check error message
        error = response.json()
        assert "planned_pickup_time" in str(error)  # Field should be mentioned
        assert "invalid" in str(error).lower()  # Should mention invalid format

    @mock.patch('services.booking_service.get_currency_converter_client_instance')
    def test_create_booking_with_currency(self, mock_get_client, auth_client, test_data):
        """Test creating a booking with a different currency"""
        # Create properly structured mock with nested client
        mock_client = Mock()
        mock_client.get_currency_rate.return_value = Decimal("0.85")
        
        mock_get_client.return_value = mock_client
        
        car_id = test_data["cars"][0].id
        user_id = test_data["users"][0].id
        
        request_data = {
            "user_id": user_id,
            "car_id": car_id,
            "start_date": "2026-01-01",
            "end_date": "2026-01-03",
            "planned_pickup_time": "10:00:00",
            "currency_code": "GBP"
        }
        
        response = auth_client.post(
            "/api/v1/bookings/",
            json=request_data
        )
        
        assert response.status_code == status.HTTP_201_CREATED
        booking = response.json()
        assert booking["user_id"] == user_id
        assert booking["car_id"] == car_id
        assert booking["currency_code"] == "GBP"
        
        # Verify the conversion was called correctly
        mock_client.get_currency_rate.assert_called_once_with("USD", "GBP")


class TestBookingDateUpdates:
    """Tests related to updating booking dates"""
    
    def test_update_booking_dates(self, auth_client, test_data):
        """Test updating booking dates"""        
        booking_id = test_data["bookings"][0].id
        
        # Calculate new dates that won't overlap with other test bookings
        new_start = date(2025, 6, 10)
        new_end = date(2025, 6, 15)
        
        update_data = {
            "start_date": str(new_start),
            "end_date": str(new_end)
        }
        
        response = auth_client.put(f"/api/v1/bookings/{booking_id}", json=update_data)
        
        # Check status code
        assert response.status_code == status.HTTP_200_OK
        
        # Check updated booking
        updated_booking = response.json()
        assert updated_booking["id"] == booking_id
        assert updated_booking["start_date"] == str(new_start)
        assert updated_booking["end_date"] == str(new_end)
        
        # Check total cost recalculation (6 days)
        car_price = float(test_data["cars"][0].price_per_day)
        expected_total = car_price * 6
        assert float(updated_booking["total_cost"]) == expected_total
    
    def test_update_pickup_date_outside_period(self, auth_client, test_data):
        """Test setting pickup date outside booking period"""        
        booking_id = test_data["bookings"][0].id
        
        # Date before booking period
        invalid_date = test_data["bookings"][0].start_date - timedelta(days=1) 
        update_data = {"pickup_date": str(invalid_date)}
        
        response = auth_client.put(f"/api/v1/bookings/{booking_id}", json=update_data)
        
        # Check status code
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        
        # Check error message
        error = response.json()
        assert "within the booking period" in error["detail"]

    def test_update_return_date_outside_period(self, auth_client, test_data, test_db):
        """Test setting return date outside booking period"""        
        booking_id = test_data["bookings"][0].id
        
        # First set pickup_date to allow setting return_date
        booking = test_db.query(Booking).filter_by(id=booking_id).first()
        booking.pickup_date = booking.start_date
        test_db.commit()
        
        # Date after booking period
        invalid_date = test_data["bookings"][0].end_date + timedelta(days=1) 
        update_data = {"return_date": str(invalid_date)}
        
        response = auth_client.put(f"/api/v1/bookings/{booking_id}", json=update_data)
        
        # Check status code
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        
        # Check error message
        error = response.json()
        assert "within the booking period" in error["detail"]
    
    def test_update_return_date_without_pickup(self, auth_client, test_data):
        """Test setting return_date without pickup_date"""        
        # Find booking without pickup_date (PLANNED status)
        booking_id = test_data["bookings"][0].id
        
        update_data = {
            "return_date": str(date.today())
        }
        
        response = auth_client.put(f"/api/v1/bookings/{booking_id}", json=update_data)
        
        # Check status code
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        
        # Check error message
        error = response.json()
        assert "Cannot set return date without a pickup date" in error["detail"]
    
    def test_update_both_pickup_and_return_dates(self, auth_client, test_data):
        """Test setting both pickup_date and return_date in the same request"""        
        booking_id = test_data["bookings"][0].id
        
        # Create dates within booking period
        booking = test_data["bookings"][0]
        pickup_date = booking.start_date + timedelta(days=1)
        return_date = booking.end_date - timedelta(days=1)
        
        update_data = {
            "pickup_date": str(pickup_date),
            "return_date": str(return_date)
        }
        
        response = auth_client.put(f"/api/v1/bookings/{booking_id}", json=update_data)
        
        # Check status code
        assert response.status_code == status.HTTP_200_OK
        
        # Check updated booking
        updated_booking = response.json()
        assert updated_booking["id"] == booking_id
        assert updated_booking["pickup_date"] == str(pickup_date)
        assert updated_booking["return_date"] == str(return_date)
        
        # Status should be updated to COMPLETED
        assert updated_booking["status"] == "COMPLETED"
    
    def test_unauthorized_booking_update(self, auth_client, test_data):
        """Test that a user cannot update another user's booking"""
        # Create a fixture that authenticates as user 2
        async def override_get_current_user():
            return test_data["users"][1]
        
        # Store original overrides
        original_overrides = app.dependency_overrides.copy()
        
        # Set the test user to user 2
        from services.auth_service import get_current_user
        app.dependency_overrides[get_current_user] = override_get_current_user
        
        try:
            # Try to update first user's booking
            booking_id = test_data["bookings"][0].id
            update_data = {"status": "CANCELED"}
            
            response = auth_client.put(f"/api/v1/bookings/{booking_id}", json=update_data)
            
            # Should be forbidden
            assert response.status_code == status.HTTP_403_FORBIDDEN
            assert "You can only access your own bookings" in response.json()["detail"]
        finally:
            # Restore original overrides
            app.dependency_overrides = original_overrides


class TestBookingStatusTransitions:
    """Tests related to booking status transitions"""
    
    @patch('services.booking_service.date')
    def test_update_status_to_active(self, mock_date, auth_client, test_data):
        """Test updating booking status to ACTIVE (which should set pickup_date)"""
        booking_id = test_data["bookings"][0].id
        booking = test_data["bookings"][0]
        
        # Mock today's date to be within the booking period
        mock_today = booking.start_date
        mock_date.today.return_value = mock_today
        # Ensure date class still works otherwise
        mock_date.side_effect = lambda *args, **kw: date(*args, **kw)
        
        update_data = {
            "status": "ACTIVE"
        }
        
        response = auth_client.put(f"/api/v1/bookings/{booking_id}", json=update_data)
        
        # Check status code
        assert response.status_code == status.HTTP_200_OK
        
        # Check updated booking
        updated_booking = response.json()
        assert updated_booking["id"] == booking_id
        assert updated_booking["status"] == "ACTIVE"
        
        # Check pickup_date was automatically set to our mocked today
        assert updated_booking["pickup_date"] == str(mock_today)
    
    @patch('services.booking_service.date')
    def test_update_status_to_canceled(self, mock_date, auth_client, test_data):
        """Test updating booking status to CANCELED"""
        booking_id = test_data["bookings"][0].id
        
        # Mock today's date to be within the booking period
        mock_today = test_data["bookings"][0].start_date
        mock_date.today.return_value = mock_today
        # Ensure date class still works otherwise
        mock_date.side_effect = lambda *args, **kw: date(*args, **kw)
        
        update_data = {"status": "CANCELED"}
        response = auth_client.put(f"/api/v1/bookings/{booking_id}", json=update_data)
        
        # Check status code
        assert response.status_code == status.HTTP_200_OK
        
        # Check updated booking status
        updated_booking = response.json()
        assert updated_booking["id"] == booking_id
        assert updated_booking["status"] == "CANCELED"
    
    @patch('services.booking_service.date')
    def test_setting_status_completed_sets_return_date(self, mock_date, auth_client, test_data, test_db):
        """Test that setting status to COMPLETED automatically sets return_date"""
        booking_id = test_data["bookings"][0].id
        
        # First set status to ACTIVE
        booking = test_db.query(Booking).filter_by(id=booking_id).first()
        booking.status = BookingStatus.ACTIVE
        booking.pickup_date = date(2024, 4, 2)
        test_db.commit()
        
        # Mock today's date
        mock_today = date(2024, 4, 3)
        mock_date.today.return_value = mock_today
        mock_date.side_effect = lambda *args, **kw: date(*args, **kw)
        
        # Update status to COMPLETED
        update_data = {"status": "COMPLETED"}
        response = auth_client.put(f"/api/v1/bookings/{booking_id}", json=update_data)
        
        # Check status code
        assert response.status_code == status.HTTP_200_OK
        
        # Check updated booking
        updated_booking = response.json()
        assert updated_booking["status"] == "COMPLETED"
        assert updated_booking["return_date"] == str(mock_today)
    
    @patch('services.booking_service.date')
    def test_transition_from_overdue_to_completed(self, mock_date, auth_client, test_data, test_db):
        """Test transitioning a booking from OVERDUE to COMPLETED when setting return_date"""
        booking_id = test_data["bookings"][0].id
        
        # Set booking to OVERDUE
        booking = test_db.query(Booking).filter_by(id=booking_id).first()
        booking.status = BookingStatus.OVERDUE
        booking.pickup_date = date(2024, 4, 2)
        test_db.commit()
        
        # Mock today
        mock_today = date(2024, 4, 15)
        mock_date.today.return_value = mock_today
        mock_date.side_effect = lambda *args, **kw: date(*args, **kw)
        
        # Update with return date 
        update_data = {"return_date": str(mock_today)}
        response = auth_client.put(f"/api/v1/bookings/{booking_id}", json=update_data)
        
        # Check status code
        assert response.status_code == status.HTTP_200_OK
        
        # Check updated booking
        updated_booking = response.json()
        assert updated_booking["status"] == "COMPLETED"
        assert updated_booking["return_date"] == str(mock_today)
    
    def test_update_completed_booking(self, auth_client, test_data, test_db):
        """Test that completed bookings cannot be updated"""
        # Set a booking to COMPLETED first
        booking_id = test_data["bookings"][0].id
        booking = test_db.query(Booking).filter_by(id=booking_id).first()
        booking.status = BookingStatus.COMPLETED
        test_db.commit()
        
        # Try to update it
        update_data = {
            "start_date": "2025-07-01"
        }
        
        response = auth_client.put(f"/api/v1/bookings/{booking_id}", json=update_data)
        
        # Check status code
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        
        # Check error message
        error = response.json()
        assert "Cannot update booking in COMPLETED state" in error["detail"]


class TestBookingRetrieval:
    """Tests related to retrieving bookings"""
    
    def test_get_all_bookings(self, admin_client, test_data):
        """Test getting all bookings as admin"""
        response = admin_client.get("/api/v1/bookings/")
        
        # Check status code
        assert response.status_code == status.HTTP_200_OK
        
        # Check response data - should be a paginated response
        response_data = response.json()
        
        # Verify the pagination structure
        assert "items" in response_data
        assert "page" in response_data
        assert "page_size" in response_data
        assert "total" in response_data
        
        # Extract the actual bookings from the 'items' field
        bookings = response_data["items"]
        assert len(bookings) == 2
        
    def test_get_my_bookings(self, auth_client, test_data):
        """Test getting current user's bookings"""
        response = auth_client.get("/api/v1/bookings/my")
        
        # Check status code
        assert response.status_code == status.HTTP_200_OK
        
        # Should be a paginated response structure
        response_data = response.json()
        assert "items" in response_data
        assert "page" in response_data
        assert "page_size" in response_data
        
        # Extract the actual bookings from the 'items' field
        bookings = response_data["items"]
        
        # Should only contain bookings for the authenticated user
        for booking in bookings:
            assert booking["user_id"] == test_data["users"][0].id
        
        # Check if we have the expected number of bookings
        # In our test data, user 1 has one booking
        user1_bookings = [b for b in test_data["bookings"] if b.user_id == test_data["users"][0].id]
        assert len(bookings) == len(user1_bookings)
        
        # Verify that the returned booking IDs match our expected bookings
        booking_ids = [booking["id"] for booking in bookings]
        expected_ids = [b.id for b in user1_bookings]
        assert set(booking_ids) == set(expected_ids)
        
    def test_get_my_bookings_empty(self, auth_client, test_data, test_db):
        """Test getting bookings when user has no bookings"""
        # Create a user with no bookings
        from models.db_models import User
        user3 = User(
            first_name="No",
            last_name="Bookings",
            email="nobookings@example.com",
            phone_number="+5555555555",
            cognito_id="cognito3"
        )
        test_db.add(user3)
        test_db.commit()
        test_db.refresh(user3)
        
        # Create a fixture that authenticates as this new user
        async def override_get_current_user():
            return user3
        
        # Store original overrides
        original_overrides = app.dependency_overrides.copy()
        
        # Set the test user to our new user with no bookings
        from services.auth_service import get_current_user
        app.dependency_overrides[get_current_user] = override_get_current_user
        
        try:
            response = auth_client.get("/api/v1/bookings/my")
            
            # Check status code
            assert response.status_code == status.HTTP_200_OK
            
            # Should return a paginated response with empty items list
            response_data = response.json()
            
            # Check pagination structure
            assert "items" in response_data
            assert "page" in response_data
            assert "page_size" in response_data
            assert "total" in response_data
            
            # Check that items is an empty list
            assert isinstance(response_data["items"], list)
            assert len(response_data["items"]) == 0
            
        finally:
            # Restore original overrides
            app.dependency_overrides = original_overrides
            
    def test_get_booking_by_id(self, auth_client, test_data):
        """Test getting a booking by ID"""        
        booking_id = test_data["bookings"][0].id
        response = auth_client.get(f"/api/v1/bookings/{booking_id}")
        
        assert response.status_code == status.HTTP_200_OK
        booking = response.json()
        assert booking["id"] == booking_id
        assert "user" in booking
        assert "car" in booking

    def test_get_booking_by_id_currency_conversion(self, auth_client, test_data, test_db):
        booking_id = test_data["bookings"][0].id
        
        # Set a known exchange rate and price for the booking
        original_usd_price = Decimal('150.53')
        exchange_rate = Decimal('1.23')  # GBP exchange rate
        
        # Update the booking in the database
        db_booking = test_db.query(Booking).filter(Booking.id == booking_id).first()
        db_booking.total_cost = original_usd_price
        db_booking.exchange_rate = exchange_rate
        test_db.commit()
        
        # Get the booking by ID
        response = auth_client.get(f"/api/v1/bookings/{booking_id}")
        assert response.status_code == status.HTTP_200_OK
        
        # Check the price conversion
        booking = response.json()
        expected_converted_price = (original_usd_price * exchange_rate).quantize(Decimal('0.00'))
        assert booking["total_cost"] == str(expected_converted_price)
        
    def test_get_booking_not_found(self, auth_client):
        """Test getting a non-existent booking"""
        non_existent_booking_id = 99999  # ID that does not exist in the test data
        response = auth_client.get(f"/api/v1/bookings/{non_existent_booking_id}")
        
        # Check status code
        assert response.status_code == status.HTTP_404_NOT_FOUND
        
        # Check error message
        error = response.json()
        assert f"Booking with ID {non_existent_booking_id} not found" in error["detail"]
        """Test getting a non-existent booking"""
        
    def test_get_booking_by_id_unauthorized(self, auth_client, test_data):
        """Test that a user cannot access another user's booking"""
        # Create a fixture that authenticates as user 2
        async def override_get_current_user():
            return test_data["users"][1]
        
        # Store original overrides
        original_overrides = app.dependency_overrides.copy()
        
        # Set the test user to user 2
        from services.auth_service import get_current_user
        app.dependency_overrides[get_current_user] = override_get_current_user
        
        try:
            # Try to access user 1's booking
            booking_id = test_data["bookings"][0].id
            response = auth_client.get(f"/api/v1/bookings/{booking_id}")
            
            # Should be forbidden
            assert response.status_code == status.HTTP_403_FORBIDDEN
            assert "You can only access your own bookings" in response.json()["detail"]
        finally:
            # Restore original overrides
            app.dependency_overrides = original_overrides


class TestBookingErrorHandling:
    """Tests related to general booking error handling"""
    
    def test_update_nonexistent_booking(self, auth_client):
        """Test updating a booking that doesn't exist"""
        non_existent_id = 999
        
        response = auth_client.get(f"/api/v1/bookings/{non_existent_id}")
        
        # Check status code
        assert response.status_code == status.HTTP_404_NOT_FOUND
        
        # Check error message
        error = response.json()
        assert f"Booking with ID {non_existent_id} not found" in error["detail"]


class TestBookingEdgeCases:
    """Tests for edge cases in booking routes"""
    
    def test_normalize_status_with_enum(self, auth_client, test_data):
        """Test normalize_status with existing enum"""
        # This directly tests the normalize_status function with an enum
        booking_id = test_data["bookings"][0].id
        response = auth_client.put(f"/api/v1/bookings/{booking_id}", json={"status": "CANCELED"})
        assert response.status_code == status.HTTP_200_OK
    
    def test_invalid_status_handling(self, auth_client, test_data):
        """Test with invalid status value"""
        booking_id = test_data["bookings"][0].id
        update_data = {"status": "INVALID_STATUS"}
        response = auth_client.put(f"/api/v1/bookings/{booking_id}", json=update_data)
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    
    @patch('services.booking_service.date')
    def test_update_only_start_date(self, mock_date, auth_client, test_data):
        """Test updating only start date"""
        booking_id = test_data["bookings"][0].id
        mock_date.today.return_value = date(2024, 3, 15)
        mock_date.side_effect = lambda *args, **kw: date(*args, **kw)
        
        # Test with a valid start date that's earlier than end date
        update_data = {"start_date": str(date(2024, 4, 2))}
        response = auth_client.put(f"/api/v1/bookings/{booking_id}", json=update_data)
        assert response.status_code == status.HTTP_200_OK
    
    def test_update_booking_overlapping_dates(self, auth_client, test_data, test_db):
        """Test updating a booking to overlap with another booking"""
        # Get two different bookings (need to ensure they use different cars initially)
        booking1 = test_data["bookings"][0]
        booking2 = test_data["bookings"][1]
        
        # Update booking2 to use the same car as booking1
        booking2.car_id = booking1.car_id
        test_db.commit()
        
        # Try to update booking1's dates to overlap with booking2
        update_data = {
            "start_date": str(booking2.start_date),
            "end_date": str(booking2.end_date)
        }
        
        response = auth_client.put(f"/api/v1/bookings/{booking1.id}", json=update_data)
        
        # Check status code and error
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "overlap with another booking" in response.json()["detail"]

    def test_pickup_after_return_date(self, auth_client, test_data, test_db):
        """Test setting pickup date after return date"""
        booking_id = test_data["bookings"][0].id
        
        # First set a return date
        booking = test_db.query(Booking).filter_by(id=booking_id).first()
        booking.status = BookingStatus.ACTIVE
        booking.pickup_date = date(2024, 4, 5)
        booking.return_date = date(2024, 4, 10)
        test_db.commit()
        
        # Now try to update pickup date to after return date
        update_data = {"pickup_date": "2024-04-12"}  # After return date
        
        response = auth_client.put(f"/api/v1/bookings/{booking_id}", json=update_data)
        
        # Check status code and error
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "Return date must be after pickup date" in response.json()["detail"]

    def test_normalize_status_edge_cases(self, auth_client, test_data):
        """Test normalize_status with non-string, non-enum values"""
        booking_id = test_data["bookings"][0].id
        
        # Test with integer status (should use default value)
        update_data = {"status": 123}  # Not a valid string or enum
        response = auth_client.put(f"/api/v1/bookings/{booking_id}", json=update_data)
        
        # Should get validation error from Pydantic
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


    @patch('services.booking_service.date')
    def test_future_pickup_date(self, mock_date, auth_client, test_data):
        """Test setting pickup date in the future"""
        booking_id = test_data["bookings"][0].id
        
        # Mock today's date
        mock_today = date(2024, 4, 1)
        mock_date.today.return_value = mock_today
        mock_date.side_effect = lambda *args, **kw: date(*args, **kw)
        
        # Try to set pickup date in the future
        future_date = mock_today + timedelta(days=1)
        update_data = {"pickup_date": str(future_date)}
        
        response = auth_client.put(f"/api/v1/bookings/{booking_id}", json=update_data)
        
        # Check status code and error
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "cannot be in the future" in response.json()["detail"]

# Example of a parameterized test for validation rules
@pytest.mark.parametrize("date_func,field,error_message", [
    (lambda b: b.start_date - timedelta(days=1), "pickup_date", "within the booking period"),
    (lambda b: b.end_date + timedelta(days=1), "pickup_date", "within the booking period"),
])
def test_date_validation_parametrized(auth_client, test_data, date_func, field, error_message):
    """Parameterized test for date validation rules"""
    booking_id = test_data["bookings"][0].id
    booking = test_data["bookings"][0]
    
    # Calculate the invalid date based on the lambda
    invalid_date = date_func(booking)
    
    # Create update data
    update_data = {field: str(invalid_date)}
    
    # Send request
    response = auth_client.put(f"/api/v1/bookings/{booking_id}", json=update_data)
    
    # Check status code
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    
    # Check error message
    error = response.json()
    assert error_message in error["detail"]

def test_get_car_price_in_currency_success():
    """Test successful price conversion"""
    with patch('services.booking_service.get_currency_converter_client_instance') as mock_get_client:
        mock_client = Mock()
        mock_client.convert.return_value = Decimal('110.00')
        
        mock_get_client.return_value = mock_client
        
        # Test the conversion
        result = get_car_price_in_currency(Decimal('100.00'), 'EUR')
        
        # Verify the result
        assert result == Decimal('110.00')
        mock_client.convert.assert_called_once_with('USD', 'EUR', Decimal('100.00'))

def test_get_car_price_in_currency_service_unavailable():
    """Test price conversion when currency service is unavailable"""
    with patch('services.booking_service.get_currency_converter_client_instance') as mock_get_client:
        # Make the client raise an exception
        mock_get_client.side_effect = CurrencyServiceUnavailableException("Currency service unavailable")
        
        # Test that the correct exception is raised
        with pytest.raises(CurrencyServiceUnavailableException) as excinfo:
            get_car_price_in_currency(Decimal('100.00'), 'EUR')
        
        # Verify the exception message
        assert "Currency service is unavailable" in str(excinfo.value)