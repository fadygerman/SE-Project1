from decimal import Decimal
from unittest import mock
from unittest.mock import Mock

from fastapi import status

from exceptions.currencies import CurrencyServiceUnavailableException


class TestCarRetrieval:
    """Tests related to retrieving cars"""
    
    def test_get_all_cars(self, auth_client, test_data):
        """Test getting all cars"""
        response = auth_client.get("/api/v1/cars/")
        
        # Check status code
        assert response.status_code == status.HTTP_200_OK
        
        # Check response data - now with pagination
        response_data = response.json()
        
        # Verify pagination structure
        assert "items" in response_data
        assert "page" in response_data
        assert "page_size" in response_data
        assert "total" in response_data
        
        # Check items
        cars = response_data["items"]
        assert len(cars) == 2
        assert cars[0]["name"] == "TestCar1"
        assert cars[1]["name"] == "TestCar2"
        
        # Check price format - should be in USD by default
        assert cars[0]["price_per_day"] == "50.00"
        assert cars[1]["price_per_day"] == "75.00"
        
        # Check availability
        assert cars[0]["is_available"] == True
        assert cars[1]["is_available"] == False
        
    def test_get_all_cars_with_usd_explicitly(self, auth_client, test_data):
        """Test getting all cars with USD explicitly specified"""
        response = auth_client.get("/api/v1/cars/?currency_code=USD")
        
        assert response.status_code == status.HTTP_200_OK
        
        # Check paginated response format
        response_data = response.json()
        
        # Verify pagination structure
        assert "items" in response_data
        assert "page" in response_data
        assert "page_size" in response_data
        assert "total" in response_data
        
        # Check the car items
        cars = response_data["items"]
        assert len(cars) == 2
        
        assert cars[0]["price_per_day"] == "50.00"
        assert cars[1]["price_per_day"] == "75.00"

    @mock.patch('services.car_service.get_currency_converter_client_instance')
    def test_get_all_cars_with_currency(self, mock_get_client, auth_client, test_data):
        """Test getting all cars with currency conversion"""
        # Create properly structured mock with nested client
        mock_client = Mock()
        mock_client.convert.side_effect = lambda from_curr, to_curr, amount: amount * 2
        
        mock_get_client.return_value = mock_client
        
        response = auth_client.get("/api/v1/cars/?currency_code=EUR")
        assert response.status_code == status.HTTP_200_OK
        
        # Get paginated response
        response_data = response.json()
        
        # Verify pagination structure
        assert "items" in response_data
        assert "page" in response_data
        assert "page_size" in response_data
        assert "total" in response_data
        
        # Check the cars
        cars = response_data["items"]
        assert len(cars) == 2
        
        # Prices should be doubled as per our mock
        assert cars[0]["price_per_day"] == "100.00"
        assert cars[1]["price_per_day"] == "150.00"
        
        assert mock_client.convert.call_count == 2
        mock_client.convert.assert_any_call("USD", "EUR", Decimal("50.00"))
        mock_client.convert.assert_any_call("USD", "EUR", Decimal("75.00"))

    @mock.patch('services.car_service.get_currency_converter_client_instance')
    def test_get_all_cars_with_currency_service_unavailable(self, mock_client_instance, auth_client, test_data):
        """Test getting all cars when currency service is unavailable"""
        # Mock the client to raise an exception
        mock_client_instance.side_effect = CurrencyServiceUnavailableException("Currency service unavailable")
        
        response = auth_client.get("/api/v1/cars/?currency_code=EUR")
        
        # Should return 503 Service Unavailable
        assert response.status_code == status.HTTP_503_SERVICE_UNAVAILABLE
        
        # Check error message
        error = response.json()
        assert "detail" in error
        assert "Currency service is unavailable" in error["detail"]

    def test_get_all_cars_with_invalid_currency(self, auth_client, test_data):
        """Test getting all cars with invalid currency code"""
        response = auth_client.get("/api/v1/cars/?currency_code=INVALID")
        
        # Check status code
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        
        # Check error message
        error = response.json()
        assert "detail" in error
        assert "Invalid currency code: INVALID" in error["detail"]

    def test_get_car_by_id(self, auth_client, test_data):
        """Test getting a car by ID"""
        car_id = test_data["cars"][0].id
        response = auth_client.get(f"/api/v1/cars/{car_id}")
        
        # Check status code
        assert response.status_code == status.HTTP_200_OK
        
        # Check response data - should be in USD by default
        car = response.json()
        assert car["id"] == car_id
        assert car["name"] == "TestCar1"
        assert car["model"] == "Model1"
        assert car["price_per_day"] == "50.00"
        assert car["is_available"] == True
        assert car["latitude"] == 40.7128
        assert car["longitude"] == -74.0060
        
    def test_get_car_by_id_with_usd_explicitly(self, auth_client, test_data):
        """Test getting a car by ID with USD explicitly specified"""
        car_id = test_data["cars"][0].id
        response = auth_client.get(f"/api/v1/cars/{car_id}?currency_code=USD")
        
        assert response.status_code == status.HTTP_200_OK
        
        car = response.json()
        assert car["price_per_day"] == "50.00"  # Should be in USD

    @mock.patch('services.car_service.get_currency_converter_client_instance')
    def test_get_car_by_id_with_currency(self, mock_get_client, auth_client, test_data):
        """Test getting a car by ID with currency conversion"""
        # Create mock client
        mock_client = Mock()
        mock_client.convert.return_value = Decimal("45.00")  # EUR value for USD 50.00
        mock_get_client.return_value = mock_client
        
        car_id = test_data["cars"][0].id
        response = auth_client.get(f"/api/v1/cars/{car_id}?currency_code=EUR")
        
        assert response.status_code == status.HTTP_200_OK
        
        car = response.json()
        assert car["id"] == car_id
        assert car["name"] == "TestCar1"
        assert car["price_per_day"] == "45.00"
        
        # Verify the convert method was called with correct parameters
        mock_client.convert.assert_called_once_with("USD", "EUR", Decimal("50.00"))

    @mock.patch('services.car_service.get_currency_converter_client_instance')
    def test_get_car_by_id_with_currency_service_unavailable(self, mock_client_instance, auth_client, test_data):
        mock_client_instance.side_effect = CurrencyServiceUnavailableException("Currency service unavailable")
        
        car_id = test_data["cars"][0].id
        response = auth_client.get(f"/api/v1/cars/{car_id}?currency_code=EUR")
        
        assert response.status_code == status.HTTP_503_SERVICE_UNAVAILABLE
        
        error = response.json()
        assert "detail" in error
        assert "Currency service is unavailable" in error["detail"]

    def test_get_car_by_id_with_invalid_currency(self, auth_client, test_data):
        """Test getting a car by ID with invalid currency"""
        car_id = test_data["cars"][0].id
        response = auth_client.get(f"/api/v1/cars/{car_id}?currency_code=INVALID")
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        
        error = response.json()
        assert "detail" in error
        assert "Invalid currency code: INVALID" in error["detail"]

    def test_get_car_not_found(self, auth_client):
        """Test getting a non-existent car"""
        non_existent_id = 999
        response = auth_client.get(f"/api/v1/cars/{non_existent_id}")
        
        # Check status code
        assert response.status_code == status.HTTP_404_NOT_FOUND
        
        # Check error message
        error = response.json()
        assert "detail" in error
        assert f"Car with ID {non_existent_id} not found" in error["detail"]