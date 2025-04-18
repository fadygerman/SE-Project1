import pytest
from fastapi import status

from models.db_models import BookingStatus, Booking
from models.currencies import Currency
from datetime import date, time, timedelta
from decimal import Decimal


class TestBookingPagination:
    """Tests for booking pagination and filtering functionality."""
    
    @pytest.fixture(scope="function")
    def setup_pagination_data(self, test_db):
        """Create additional bookings for pagination testing"""
        today = date.today()
        
        # Create additional bookings for pagination testing
        additional_bookings = []
        for i in range(5, 25):
            additional_booking = Booking(
                user_id=1 if i % 2 == 0 else 2,  # Alternate between users
                car_id=((i - 5) % 2) + 1,  # Cycle through cars 1-2
                start_date=today + timedelta(days=i),
                end_date=today + timedelta(days=i + 5),
                planned_pickup_time=time(12, 0),
                total_cost=Decimal("300.00"),
                currency_code=Currency.USD,
                exchange_rate=Decimal("1.0"),
                status=BookingStatus.PLANNED
            )
            additional_bookings.append(additional_booking)
        
        test_db.add_all(additional_bookings)
        test_db.commit()
        
        yield
        
        # Clean up added bookings
        for booking in additional_bookings:
            test_db.delete(booking)
        test_db.commit()
    
    def test_get_all_bookings_pagination(self, admin_client, setup_pagination_data):
        """Test basic pagination for all bookings"""
        # First page with 10 items
        response = admin_client.get("/api/v1/bookings/?page=1&page_size=10")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        # Check pagination metadata
        assert data["page"] == 1
        assert data["page_size"] == 10
        assert data["total"] >= 20  # At least 20 total bookings with our additions
        assert len(data["items"]) == 10
        
        # Second page with 10 items
        response = admin_client.get("/api/v1/bookings/?page=2&page_size=10")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        assert data["page"] == 2
        assert len(data["items"]) > 0  # Should have some items
        
        # Third page with remaining items (if any)
        if data["total"] > 20:
            response = admin_client.get("/api/v1/bookings/?page=3&page_size=10")
            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            assert data["page"] == 3
    
    def test_get_all_bookings_with_status_filter(self, admin_client, setup_pagination_data):
        """Test filtering bookings by status"""
        response = admin_client.get("/api/v1/bookings/?status=ACTIVE")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        # All returned bookings should have ACTIVE status
        for booking in data["items"]:
            assert booking["status"] == "ACTIVE"
    
    def test_get_all_bookings_with_car_id_filter(self, admin_client, test_data, setup_pagination_data):
        """Test filtering bookings by car_id"""
        car_id = test_data["cars"][0].id
        response = admin_client.get(f"/api/v1/bookings/?car_id={car_id}")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        # All returned bookings should have the specified car_id
        for booking in data["items"]:
            assert booking["car_id"] == car_id
    
    def test_get_all_bookings_with_date_filters(self, admin_client, setup_pagination_data):
        """Test filtering bookings by date ranges"""
        today = date.today()
        
        # Test start_date_from filter
        start_date = (today + timedelta(days=10)).isoformat()
        response = admin_client.get(f"/api/v1/bookings/?start_date_from={start_date}")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        for booking in data["items"]:
            booking_start_date = booking["start_date"]
            assert booking_start_date >= start_date
    
    def test_get_all_bookings_with_sorting(self, admin_client, setup_pagination_data):
        """Test sorting bookings by different fields"""
        # Sort by start_date ascending
        response = admin_client.get("/api/v1/bookings/?sort_by=start_date&sort_order=asc")
        assert response.status_code == status.HTTP_200_OK
        data_asc = response.json()
        
        # Verify ascending order
        for i in range(1, len(data_asc["items"])):
            assert data_asc["items"][i-1]["start_date"] <= data_asc["items"][i]["start_date"]
        
        # Sort by start_date descending
        response = admin_client.get("/api/v1/bookings/?sort_by=start_date&sort_order=desc")
        assert response.status_code == status.HTTP_200_OK
        data_desc = response.json()
        
        # Verify descending order
        for i in range(1, len(data_desc["items"])):
            assert data_desc["items"][i-1]["start_date"] >= data_desc["items"][i]["start_date"]
    
    def test_get_my_bookings_pagination(self, auth_client, setup_pagination_data):
        """Test pagination for my bookings endpoint"""
        # First page of my bookings
        response = auth_client.get("/api/v1/bookings/my?page=1&page_size=5")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        # Check pagination metadata
        assert data["page"] == 1
        assert data["page_size"] == 5
        # We expect to see the user's bookings
        assert data["total"] > 0
    
    def test_combined_filters(self, admin_client, setup_pagination_data):
        """Test combining multiple filters"""
        today = date.today()
        
        # Combine status and date filter
        start_date = (today + timedelta(days=5)).isoformat()
        response = admin_client.get(f"/api/v1/bookings/?status=PLANNED&start_date_from={start_date}")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        # Check that all returned bookings match both filter criteria
        for booking in data["items"]:
            assert booking["status"] == "PLANNED"
            assert booking["start_date"] >= start_date
    
    def test_invalid_pagination_params(self, admin_client, setup_pagination_data):
        """Test behavior with invalid pagination parameters"""
        # Invalid page number
        response = admin_client.get("/api/v1/bookings/?page=0")
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY  # Validation error
        
        # Invalid page size
        response = admin_client.get("/api/v1/bookings/?page_size=0")
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        
        response = admin_client.get("/api/v1/bookings/?page_size=101")  # Exceeds maximum
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_invalid_date_format_handling(self, admin_client, setup_pagination_data):
        """Test handling of invalid date format in filter parameters"""
        # Test invalid start_date_from format
        response = admin_client.get("/api/v1/bookings/?start_date_from=2024/04/15")
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        error = response.json()
        assert "Invalid date format for 'start_date_from'" in error["detail"]
        
        # Test invalid start_date_to format
        response = admin_client.get("/api/v1/bookings/?start_date_to=15-04-2024")
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "Invalid date format for 'start_date_to'" in response.json()["detail"]
        
        # Test invalid end_date_from format
        response = admin_client.get("/api/v1/bookings/?end_date_from=April 15, 2024")
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "Invalid date format for 'end_date_from'" in response.json()["detail"]
        
        # Test invalid end_date_to format
        response = admin_client.get("/api/v1/bookings/?end_date_to=15.04.2024")
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "Invalid date format for 'end_date_to'" in response.json()["detail"]

    def test_invalid_date_format_in_my_bookings(self, auth_client, setup_pagination_data):
        """Test handling of invalid date format in my bookings filter parameters"""
        response = auth_client.get("/api/v1/bookings/my?start_date_from=not-a-date")
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "Invalid date format" in response.json()["detail"]

    def test_multiple_filter_parameters_with_one_invalid(self, admin_client, setup_pagination_data):
        """Test that invalid date format is caught even with multiple parameters"""
        response = admin_client.get("/api/v1/bookings/?status=PLANNED&start_date_from=2024-04-15&end_date_to=invalid")
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "Invalid date format for 'end_date_to'" in response.json()["detail"]