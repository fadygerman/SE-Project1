import pytest
from fastapi import status

from models.db_models import Car
from decimal import Decimal


class TestCarPagination:
    """Tests for car pagination and filtering functionality."""
    
    @pytest.fixture(scope="function")
    def setup_car_pagination_data(self, test_db):
        """Create additional cars for pagination testing"""
        # Create additional cars for pagination testing
        additional_cars = []
        for i in range(5, 25):
            additional_car = Car(
                name=f"Car {i}",
                model=f"Model {i}",
                price_per_day=Decimal(f"{50 + i}.00"),
                is_available=i % 2 == 0  # Every other car is available
            )
            additional_cars.append(additional_car)
        
        test_db.add_all(additional_cars)
        test_db.commit()
        
        yield
        
        # Clean up added cars
        for car in additional_cars:
            test_db.delete(car)
        test_db.commit()
    
    def test_get_cars_pagination(self, auth_client, setup_car_pagination_data):
        """Test basic pagination for cars"""
        # First page with 10 items
        response = auth_client.get("/api/v1/cars/?page=1&page_size=10")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        # Check pagination metadata
        assert data["page"] == 1
        assert data["page_size"] == 10
        assert data["total"] >= 20  # At least 20 total cars with our additions
        assert len(data["items"]) == 10
        
        # Second page with 10 items
        response = auth_client.get("/api/v1/cars/?page=2&page_size=10")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        assert data["page"] == 2
        assert len(data["items"]) > 0  # Should have some items
    
    def test_get_cars_with_name_filter(self, auth_client, setup_car_pagination_data):
        """Test filtering cars by name"""
        # Test name filter
        response = auth_client.get("/api/v1/cars/?name=Car 10")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        # Should find cars with "Car 10" in name
        assert len(data["items"]) >= 1
        assert any("Car 10" in car["name"] for car in data["items"])
    
    def test_get_cars_with_availability_filter(self, auth_client, setup_car_pagination_data):
        """Test filtering cars by availability"""
        # Test availability filter
        response = auth_client.get("/api/v1/cars/?available_only=true")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        # All returned cars should be available
        for car in data["items"]:
            assert car["is_available"] == True
    
    def test_get_cars_with_sorting(self, auth_client, setup_car_pagination_data):
        """Test sorting cars by different fields"""
        # Sort by price ascending
        response = auth_client.get("/api/v1/cars/?sort_by=price_per_day&sort_order=asc")
        assert response.status_code == status.HTTP_200_OK
        data_asc = response.json()
        
        # Verify ascending order
        for i in range(1, len(data_asc["items"])):
            assert float(data_asc["items"][i-1]["price_per_day"]) <= float(data_asc["items"][i]["price_per_day"])
        
        # Sort by price descending
        response = auth_client.get("/api/v1/cars/?sort_by=price_per_day&sort_order=desc")
        assert response.status_code == status.HTTP_200_OK
        data_desc = response.json()
        
        # Verify descending order
        for i in range(1, len(data_desc["items"])):
            assert float(data_desc["items"][i-1]["price_per_day"]) >= float(data_desc["items"][i]["price_per_day"])
    
    def test_combined_filters(self, auth_client, setup_car_pagination_data):
        """Test combining multiple filters"""
        # Combine availability and sorting
        response = auth_client.get("/api/v1/cars/?available_only=true&sort_by=price_per_day&sort_order=desc")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        # Check that all returned cars meet both filter criteria
        for i in range(1, len(data["items"])):
            assert data["items"][i]["is_available"] == True
            if i > 0:
                assert float(data["items"][i-1]["price_per_day"]) >= float(data["items"][i]["price_per_day"])
    
    def test_invalid_pagination_params(self, auth_client, setup_car_pagination_data):
        """Test behavior with invalid pagination parameters"""
        # Invalid page number
        response = auth_client.get("/api/v1/cars/?page=0")
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        
        # Invalid page size
        response = auth_client.get("/api/v1/cars/?page_size=0")
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        
        response = auth_client.get("/api/v1/cars/?page_size=101")  # Exceeds maximum
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY