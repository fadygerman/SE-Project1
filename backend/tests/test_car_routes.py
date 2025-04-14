from decimal import Decimal
from unittest import mock

from fastapi import status


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
        
        # Check price format - should be in USD by default
        assert cars[0]["price_per_day"] == "50.00"
        assert cars[1]["price_per_day"] == "75.00"
        
        # Check availability
        assert cars[0]["is_available"] == True
        assert cars[1]["is_available"] == False
        
    def test_get_all_cars_with_usd_explicitly(self, client, test_data):
        """Test getting all cars with USD explicitly specified"""
        response = client.get("/api/v1/cars/?currency_code=USD")
        
        assert response.status_code == status.HTTP_200_OK
        
        cars = response.json()
        assert len(cars) == 2
        
        assert cars[0]["price_per_day"] == "50.00"
        assert cars[1]["price_per_day"] == "75.00"

    @mock.patch('currency_converter.client.CurrencyConverterClient.convert')
    def test_get_all_cars_with_currency(self, mock_convert, client, test_data):
        """Test getting all cars with currency conversion
        ATTENTION: Currency converter must be running to pass this test
        """
        # Mock the convert method to return a predefined value (2x the input value for easy testing)
        mock_convert.side_effect = lambda from_curr, to_curr, amount: amount * 2
        
        response = client.get("/api/v1/cars/?currency_code=EUR")
        assert response.status_code == status.HTTP_200_OK
        
        cars = response.json()
        assert len(cars) == 2
        
        # Prices should be doubled as per our mock
        assert cars[0]["price_per_day"] == "100.00"
        assert cars[1]["price_per_day"] == "150.00"
        
        assert mock_convert.call_count == 2
        mock_convert.assert_any_call("USD", "EUR", Decimal("50.00"))
        mock_convert.assert_any_call("USD", "EUR", Decimal("75.00"))

    def test_get_all_cars_with_invalid_currency(self, client, test_data):
        """Test getting all cars with invalid currency code"""
        response = client.get("/api/v1/cars/?currency_code=INVALID")
        
        # Check status code
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        
        # Check error message
        error = response.json()
        assert "detail" in error
        assert "Invalid currency code: INVALID" in error["detail"]

    def test_get_car_by_id(self, client, test_data):
        """Test getting a car by ID"""
        car_id = test_data["cars"][0].id
        response = client.get(f"/api/v1/cars/{car_id}")
        
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
        
    def test_get_car_by_id_with_usd_explicitly(self, client, test_data):
        """Test getting a car by ID with USD explicitly specified"""
        car_id = test_data["cars"][0].id
        response = client.get(f"/api/v1/cars/{car_id}?currency_code=USD")
        
        assert response.status_code == status.HTTP_200_OK
        
        car = response.json()
        assert car["price_per_day"] == "50.00"  # Should be in USD

    @mock.patch('currency_converter.client.CurrencyConverterClient.convert')
    def test_get_car_by_id_with_currency(self, mock_convert, client, test_data):
        """ATTENTION: Currency converter must be running to pass this test"""
        mock_convert.return_value = Decimal("45.00")  # EUR value for USD 50.00
        
        car_id = test_data["cars"][0].id
        response = client.get(f"/api/v1/cars/{car_id}?currency_code=EUR")
        assert response.status_code == status.HTTP_200_OK
        
        car = response.json()
        assert car["id"] == car_id
        assert car["name"] == "TestCar1"
        assert car["price_per_day"] == "45.00"
        
        # Verify the convert method was called with correct parameters
        mock_convert.assert_called_once_with("USD", "EUR", Decimal("50.00"))

    def test_get_car_by_id_with_invalid_currency(self, client, test_data):
        car_id = test_data["cars"][0].id
        response = client.get(f"/api/v1/cars/{car_id}?currency_code=INVALID")
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        
        error = response.json()
        assert "detail" in error
        assert "Invalid currency code: INVALID" in error["detail"]

    def test_get_car_not_found(self, client):
        """Test getting a non-existent car"""
        non_existent_id = 999
        response = client.get(f"/api/v1/cars/{non_existent_id}")
        
        # Check status code
        assert response.status_code == status.HTTP_404_NOT_FOUND
        
        # Check error message
        error = response.json()
        assert "detail" in error
        assert f"Car with ID {non_existent_id} not found" in error["detail"]