from unittest.mock import patch

from fastapi import status

from models.db_models import User
from utils.auth_cognito import get_current_user


class TestAuthRoutes:
    """Tests for auth routes and Cognito integration endpoints"""

    def test_register_cognito_user(self, client, test_db):
        """Test registering a new user from Cognito data"""
        user_data = {
            "first_name": "Jane",
            "last_name": "Doe",
            "email": "jane.doe@example.com",
            "phone_number": "+12345678901",
            "cognito_id": "cognito-id-12345"
        }
        
        response = client.post("/api/v1/auth/register-cognito-user", json=user_data)
        
        # Check status code
        assert response.status_code == status.HTTP_201_CREATED
        
        # Check response data
        result = response.json()
        assert "id" in result
        assert result["message"] == "User registered successfully"
        
        # Verify user was created in the database
        user = test_db.query(User).filter(User.cognito_id == user_data["cognito_id"]).first()
        assert user is not None
        assert user.email == user_data["email"]
        assert user.first_name == user_data["first_name"]
        assert user.last_name == user_data["last_name"]
        assert user.phone_number == user_data["phone_number"]
        # No password_hash field in the model anymore
    
    def test_register_duplicate_cognito_user(self, client, test_db, test_data):
        """Test attempting to register a user with an existing cognito_id"""
        # Use cognito_id from an existing test user
        existing_user = test_data["users"][0]
        
        user_data = {
            "first_name": "Another",
            "last_name": "User",
            "email": "another@example.com",
            "phone_number": "+9876543210",
            "cognito_id": existing_user.cognito_id  # Use existing cognito_id
        }
        
        response = client.post("/api/v1/auth/register-cognito-user", json=user_data)
        
        # Check status code - should be bad request
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        
        # Check error message
        error = response.json()
        assert "User already exists" in error["detail"]
    
    def test_public_endpoint(self, client):
        """Test accessing public endpoint (no authentication required)"""
        response = client.get("/api/v1/auth/public")
        
        # Check status code
        assert response.status_code == status.HTTP_200_OK
        
        # Check response data
        result = response.json()
        assert result["message"] == "This is a public endpoint"
        
    @patch('utils.auth_cognito.get_current_user')
    def test_protected_endpoint(self, mock_get_current_user, client, test_data):
        """Test accessing protected endpoint with valid authentication"""
        # Mock the authentication to return a valid user
        user = test_data["users"][0]
        mock_get_current_user.return_value = user
        
        response = client.get("/api/v1/auth/protected")
        
        # Check status code
        assert response.status_code == status.HTTP_200_OK
        
        # Check response data
        result = response.json()
        assert result["message"] == "Authentication successful"
        assert result["user_id"] == user.id
        assert result["email"] == user.email
        
    def test_protected_endpoint_no_auth(self, client):
        """Test accessing protected endpoint without authentication"""
        # No authentication header provided
        response = client.get("/api/v1/auth/protected")
        
        # Should return 401 Unauthorized or 403 Forbidden
        assert response.status_code in [status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN]