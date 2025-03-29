import pytest
from fastapi import status
from decimal import Decimal

class TestCarRetrieval:
    """Tests related to retrieving cars"""
    
    def test_get_all_cars(self, client, test_data):
        """Test getting all cars"""
        response = client.get("/api/v1/cars/")
        
        # Check status code
        assert response.status_code == status.HTTP_200_OK
        
        # Check response data
        cars = response.json()
        assert len(cars) == 2
        assert cars[0]["name"] == "TestCar1"
        assert cars[1]["name"] == "TestCar2"
        
        # Check price format
        assert cars[0]["price_per_day"] == "50.00"
        assert cars[1]["price_per_day"] == "75.00"
        
        # Check availability
        assert cars[0]["is_available"] == True
        assert cars[1]["is_available"] == False

    def test_get_car_by_id(self, client, test_data):
        """Test getting a car by ID"""
        car_id = test_data["cars"][0].id
        response = client.get(f"/api/v1/cars/{car_id}")
        
        # Check status code
        assert response.status_code == status.HTTP_200_OK
        
        # Check response data
        car = response.json()
        assert car["id"] == car_id
        assert car["name"] == "TestCar1"
        assert car["model"] == "Model1"
        assert car["price_per_day"] == "50.00"
        assert car["is_available"] == True
        assert car["latitude"] == 40.7128
        assert car["longitude"] == -74.0060

    def test_get_car_not_found(self, client, test_data):
        """Test getting a non-existent car"""
        non_existent_id = 999
        response = client.get(f"/api/v1/cars/{non_existent_id}")
        
        # Check status code
        assert response.status_code == status.HTTP_404_NOT_FOUND
        
        # Check error message
        error = response.json()
        assert "detail" in error
        assert f"Car with ID {non_existent_id} not found" in error["detail"]