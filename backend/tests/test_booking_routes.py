import pytest
from fastapi import status
from datetime import date, timedelta
from decimal import Decimal
from unittest.mock import patch

from models.db_models import BookingStatus, Booking

class TestBookingCreation:
    """Tests related to creating bookings"""
    
    @patch('models.models.date')
    def test_create_valid_booking(self, mock_date, client, test_data):
        """Test successfully creating a booking"""
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
            "user_id": user_id,
            "car_id": car_id,
            "start_date": str(start_date),
            "end_date": str(end_date)
        }
        
        response = client.post("/api/v1/bookings/", json=booking_data)
        
        # Check status code
        assert response.status_code == status.HTTP_201_CREATED
        
        # Check response data
        created_booking = response.json()
        assert created_booking["user_id"] == user_id
        assert created_booking["car_id"] == car_id
        assert created_booking["start_date"] == str(start_date)
        assert created_booking["end_date"] == str(end_date)
        assert created_booking["status"] == "PLANNED"
        
        # Check total cost calculation (4 days × car price)
        car_price = float(test_data["cars"][0].price_per_day)
        expected_total = car_price * 4
        assert float(created_booking["total_cost"]) == expected_total

    def test_create_booking_car_not_found(self, client, test_data):
        """Test creating a booking with non-existent car ID"""
        booking_data = {
            "user_id": test_data["users"][0].id,
            "car_id": 999,  # Non-existent car ID
            "start_date": "2025-06-01",
            "end_date": "2025-06-05"
        }
        
        response = client.post("/api/v1/bookings/", json=booking_data)
        
        # Check status code
        assert response.status_code == status.HTTP_404_NOT_FOUND
        
        # Check error message
        error = response.json()
        assert "Car with ID 999 not found" in error["detail"]

    def test_create_booking_unavailable_car(self, client, test_data):
        """Test creating a booking for an unavailable car"""
        # Car 2 is marked as unavailable in test data
        unavailable_car_id = test_data["cars"][1].id
        
        booking_data = {
            "user_id": test_data["users"][0].id,
            "car_id": unavailable_car_id,
            "start_date": "2025-06-01",
            "end_date": "2025-06-05"
        }
        
        response = client.post("/api/v1/bookings/", json=booking_data)
        
        # Check status code
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        
        # Check error message
        error = response.json()
        assert f"Car with ID {unavailable_car_id} is not available" in error["detail"]

    @patch('services.booking_service.date')
    def test_create_booking_start_date_today(self, mock_date, client, test_data):
        # Setup mock for date.today()
        mock_today = date(2024, 5, 15)
        mock_date.today.return_value = mock_today
        # Ensure date class still works otherwise
        mock_date.side_effect = lambda *args, **kw: date(*args, **kw)
        
        booking_data = {
            "user_id": test_data["users"][0].id,
            "car_id": test_data["cars"][0].id,
            "start_date": str(mock_today),     # Today's date
            "end_date": str(mock_today + timedelta(days=5))
        }
        
        response = client.post("/api/v1/bookings/", json=booking_data)
        
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        
        error = response.json()
        assert "Start date must be tomorrow or later" in str(error)
    
    @patch('services.booking_service.date')
    def test_create_booking_start_date_past(self, mock_date, client, test_data):
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
            "end_date": str(mock_today + timedelta(days=5))
        }
        
        response = client.post("/api/v1/bookings/", json=booking_data)
        
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        
        error = response.json()
        assert "Start date must be tomorrow or later" in str(error)

    @patch('models.models.date')
    def test_create_booking_overlapping_dates(self, mock_date, client, test_data):
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
            "end_date": str(existing_booking.end_date + timedelta(days=5))  # Extended end date
        }
        
        response = client.post("/api/v1/bookings/", json=booking_data)
        
        # Check status code
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        
        # Check error message
        error = response.json()
        assert "already booked for the selected dates" in error["detail"]

    def test_create_booking_invalid_dates(self, client, test_data):
        """Test creating a booking with end date before start date"""
        booking_data = {
            "user_id": test_data["users"][0].id,
            "car_id": test_data["cars"][0].id,
            "start_date": "2025-06-05",  # Later date
            "end_date": "2025-06-01"     # Earlier date
        }
        
        response = client.post("/api/v1/bookings/", json=booking_data)
        
        # Check status code and error
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        
        # Pydantic validation should catch this
        error = response.json()
        assert "End date must be after start date" in str(error)

    @patch('models.models.date')
    def test_create_booking_without_end_date(self, mock_date, client, test_data):
        """Test creating a booking without providing an end_date"""
        # Setup mock for date.today()
        mock_today = date(2024, 5, 15)
        mock_date.today.return_value = mock_today
        mock_date.side_effect = lambda *args, **kw: date(*args, **kw)
        
        # Create a booking data without end_date
        booking_data = {
            "user_id": test_data["users"][0].id,
            "car_id": test_data["cars"][0].id,
            "end_date": str(mock_today + timedelta(days=5))  # Valid future date
            # No end_date provided
        }
        
        response = client.post("/api/v1/bookings/", json=booking_data)
        
        # Check status code - should be validation error
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        
        # Check error message
        error = response.json()
        assert "end_date" in str(error)  # Field should be mentioned in the error
        assert "field required" in str(error).lower()  # Standard Pydantic missing field message


class TestBookingDateUpdates:
    """Tests related to updating booking dates"""
    
    def test_update_booking_dates(self, client, test_data):
        """Test updating booking dates"""
        booking_id = test_data["bookings"][0].id
        
        # Calculate new dates that won't overlap with other test bookings
        new_start = date(2025, 6, 10)
        new_end = date(2025, 6, 15)
        
        update_data = {
            "start_date": str(new_start),
            "end_date": str(new_end)
        }
        
        response = client.put(f"/api/v1/bookings/{booking_id}", json=update_data)
        
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
    
    def test_update_pickup_date_outside_period(self, client, test_data):
        """Test setting pickup date outside booking period"""
        booking_id = test_data["bookings"][0].id
        
        # Date before booking period
        invalid_date = test_data["bookings"][0].start_date - timedelta(days=1) 
        update_data = {"pickup_date": str(invalid_date)}
        
        response = client.put(f"/api/v1/bookings/{booking_id}", json=update_data)
        
        # Check status code
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        
        # Check error message
        error = response.json()
        assert "within the booking period" in error["detail"]

    def test_update_return_date_outside_period(self, client, test_data, test_db):
        """Test setting return date outside booking period"""
        booking_id = test_data["bookings"][0].id
        
        # First set pickup_date to allow setting return_date
        booking = test_db.query(Booking).filter_by(id=booking_id).first()
        booking.pickup_date = booking.start_date
        test_db.commit()
        
        # Date after booking period
        invalid_date = test_data["bookings"][0].end_date + timedelta(days=1) 
        update_data = {"return_date": str(invalid_date)}
        
        response = client.put(f"/api/v1/bookings/{booking_id}", json=update_data)
        
        # Check status code
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        
        # Check error message
        error = response.json()
        assert "within the booking period" in error["detail"]
    
    def test_update_return_date_without_pickup(self, client, test_data):
        """Test setting return_date without pickup_date"""
        # Find booking without pickup_date (PLANNED status)
        booking_id = test_data["bookings"][0].id
        
        update_data = {
            "return_date": str(date.today())
        }
        
        response = client.put(f"/api/v1/bookings/{booking_id}", json=update_data)
        
        # Check status code
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        
        # Check error message
        error = response.json()
        assert "Cannot set return date without a pickup date" in error["detail"]
    
    def test_update_both_pickup_and_return_dates(self, client, test_data):
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
        
        response = client.put(f"/api/v1/bookings/{booking_id}", json=update_data)
        
        # Check status code
        assert response.status_code == status.HTTP_200_OK
        
        # Check updated booking
        updated_booking = response.json()
        assert updated_booking["id"] == booking_id
        assert updated_booking["pickup_date"] == str(pickup_date)
        assert updated_booking["return_date"] == str(return_date)
        
        # Status should be updated to COMPLETED
        assert updated_booking["status"] == "COMPLETED"


class TestBookingStatusTransitions:
    """Tests related to booking status transitions"""
    
    @patch('services.booking_service.date')
    def test_update_status_to_active(self, mock_date, client, test_data):
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
        
        response = client.put(f"/api/v1/bookings/{booking_id}", json=update_data)
        
        # Check status code
        assert response.status_code == status.HTTP_200_OK
        
        # Check updated booking
        updated_booking = response.json()
        assert updated_booking["id"] == booking_id
        assert updated_booking["status"] == "ACTIVE"
        
        # Check pickup_date was automatically set to our mocked today
        assert updated_booking["pickup_date"] == str(mock_today)
    
    @patch('services.booking_service.date')
    def test_update_status_to_canceled(self, mock_date, client, test_data):
        """Test updating booking status to CANCELED"""
        booking_id = test_data["bookings"][0].id
        
        # Mock today's date to be within the booking period
        mock_today = test_data["bookings"][0].start_date
        mock_date.today.return_value = mock_today
        # Ensure date class still works otherwise
        mock_date.side_effect = lambda *args, **kw: date(*args, **kw)
        
        update_data = {"status": "CANCELED"}
        response = client.put(f"/api/v1/bookings/{booking_id}", json=update_data)
        
        # Check status code
        assert response.status_code == status.HTTP_200_OK
        
        # Check updated booking status
        updated_booking = response.json()
        assert updated_booking["id"] == booking_id
        assert updated_booking["status"] == "CANCELED"
    
    @patch('services.booking_service.date')
    def test_setting_status_completed_sets_return_date(self, mock_date, client, test_data, test_db):
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
        response = client.put(f"/api/v1/bookings/{booking_id}", json=update_data)
        
        # Check status code
        assert response.status_code == status.HTTP_200_OK
        
        # Check updated booking
        updated_booking = response.json()
        assert updated_booking["status"] == "COMPLETED"
        assert updated_booking["return_date"] == str(mock_today)
    
    @patch('services.booking_service.date')
    def test_transition_from_overdue_to_completed(self, mock_date, client, test_data, test_db):
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
        response = client.put(f"/api/v1/bookings/{booking_id}", json=update_data)
        
        # Check status code
        assert response.status_code == status.HTTP_200_OK
        
        # Check updated booking
        updated_booking = response.json()
        assert updated_booking["status"] == "COMPLETED"
        assert updated_booking["return_date"] == str(mock_today)
    
    def test_update_completed_booking(self, client, test_data, test_db):
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
        
        response = client.put(f"/api/v1/bookings/{booking_id}", json=update_data)
        
        # Check status code
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        
        # Check error message
        error = response.json()
        assert "Cannot update booking in COMPLETED state" in error["detail"]


class TestBookingErrorHandling:
    """Tests related to general booking error handling"""
    
    def test_update_nonexistent_booking(self, client):
        """Test updating a booking that doesn't exist"""
        non_existent_id = 999
        
        update_data = {
            "status": "ACTIVE"
        }
        
        response = client.put(f"/api/v1/bookings/{non_existent_id}", json=update_data)
        
        # Check status code
        assert response.status_code == status.HTTP_404_NOT_FOUND
        
        # Check error message
        error = response.json()
        assert f"Booking with ID {non_existent_id} not found" in error["detail"]


class TestBookingRetrieval:
    """Tests related to retrieving bookings"""
    
    def test_get_all_bookings(self, client, test_data):
        """Test getting all bookings"""
        response = client.get("/api/v1/bookings/")
        
        # Check status code
        assert response.status_code == status.HTTP_200_OK
        
        # Check response data
        bookings = response.json()
        assert len(bookings) == 2
        
        # Check first booking details
        assert bookings[0]["user_id"] == test_data["users"][0].id
        assert bookings[0]["car_id"] == test_data["cars"][0].id
        assert bookings[0]["status"] == "PLANNED"
        
        # Check second booking details
        assert bookings[1]["user_id"] == test_data["users"][1].id
        assert bookings[1]["status"] == "ACTIVE"

    def test_get_booking_by_id(self, client, test_data):
        """Test getting a booking by ID"""
        booking_id = test_data["bookings"][0].id
        response = client.get(f"/api/v1/bookings/{booking_id}")
        
        assert response.status_code == status.HTTP_200_OK
        booking = response.json()
        assert booking["id"] == booking_id
        assert "user" in booking
        assert "car" in booking

    def test_get_booking_not_found(self, client):
        """Test getting a non-existent booking"""
        non_existent_id = 999
        response = client.get(f"/api/v1/bookings/{non_existent_id}")
        
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert f"Booking with ID {non_existent_id} not found" in response.json()["detail"]


class TestBookingEdgeCases:
    """Tests for edge cases in booking routes"""
    
    def test_normalize_status_with_enum(self, client, test_data):
        """Test normalize_status with existing enum"""
        # This directly tests the normalize_status function with an enum
        booking_id = test_data["bookings"][0].id
        update_data = {"status": BookingStatus.CANCELED}
        response = client.put(f"/api/v1/bookings/{booking_id}", json={"status": "CANCELED"})
        assert response.status_code == status.HTTP_200_OK
    
    def test_invalid_status_handling(self, client, test_data):
        """Test with invalid status value"""
        booking_id = test_data["bookings"][0].id
        update_data = {"status": "INVALID_STATUS"}
        response = client.put(f"/api/v1/bookings/{booking_id}", json=update_data)
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    
    @patch('services.booking_service.date')
    def test_update_only_start_date(self, mock_date, client, test_data):
        """Test updating only start date"""
        booking_id = test_data["bookings"][0].id
        mock_date.today.return_value = date(2024, 3, 15)
        mock_date.side_effect = lambda *args, **kw: date(*args, **kw)
        
        # Test with a valid start date that's earlier than end date
        update_data = {"start_date": str(date(2024, 4, 2))}
        response = client.put(f"/api/v1/bookings/{booking_id}", json=update_data)
        assert response.status_code == status.HTTP_200_OK
    
    def test_update_booking_overlapping_dates(self, client, test_data, test_db):
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
        
        response = client.put(f"/api/v1/bookings/{booking1.id}", json=update_data)
        
        # Check status code and error
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "overlap with another booking" in response.json()["detail"]

    def test_pickup_after_return_date(self, client, test_data, test_db):
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
        
        response = client.put(f"/api/v1/bookings/{booking_id}", json=update_data)
        
        # Check status code and error
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "Return date must be after pickup date" in response.json()["detail"]

    def test_normalize_status_edge_cases(self, client, test_data):
        """Test normalize_status with non-string, non-enum values"""
        booking_id = test_data["bookings"][0].id
        
        # Test with integer status (should use default value)
        update_data = {"status": 123}  # Not a valid string or enum
        response = client.put(f"/api/v1/bookings/{booking_id}", json=update_data)
        
        # Should get validation error from Pydantic
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


    @patch('services.booking_service.date')
    def test_future_pickup_date(self, mock_date, client, test_data):
        """Test setting pickup date in the future"""
        booking_id = test_data["bookings"][0].id
        
        # Mock today's date
        mock_today = date(2024, 4, 1)
        mock_date.today.return_value = mock_today
        mock_date.side_effect = lambda *args, **kw: date(*args, **kw)
        
        # Try to set pickup date in the future
        future_date = mock_today + timedelta(days=1)
        update_data = {"pickup_date": str(future_date)}
        
        response = client.put(f"/api/v1/bookings/{booking_id}", json=update_data)
        
        # Check status code and error
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "cannot be in the future" in response.json()["detail"]

# Example of a parameterized test for validation rules
@pytest.mark.parametrize("date_func,field,error_message", [
    (lambda b: b.start_date - timedelta(days=1), "pickup_date", "within the booking period"),
    (lambda b: b.end_date + timedelta(days=1), "pickup_date", "within the booking period"),
])
def test_date_validation_parametrized(client, test_data, date_func, field, error_message):
    """Parameterized test for date validation rules"""
    booking_id = test_data["bookings"][0].id
    booking = test_data["bookings"][0]
    
    # Calculate the invalid date based on the lambda
    invalid_date = date_func(booking)
    
    # Create update data
    update_data = {field: str(invalid_date)}
    
    # Send request
    response = client.put(f"/api/v1/bookings/{booking_id}", json=update_data)
    
    # Check status code
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    
    # Check error message
    error = response.json()
    assert error_message in error["detail"]