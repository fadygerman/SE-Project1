import pytest
from fastapi import status

class TestAuthRoutes:
    """Tests related to authentication routes"""
    
    def test_public_endpoint(self, client):
        """Test accessing a public endpoint"""
        response = client.get("/api/v1/auth/public")
        
        # Check status code
        assert response.status_code == status.HTTP_200_OK
        
        # Check response data
        assert response.json() == {"message": "This is a public endpoint"}
    
    def test_protected_endpoint(self, auth_client):
        """Test accessing a protected endpoint with authentication"""
        response = auth_client.get("/api/v1/auth/protected")
        
        # Check status code
        assert response.status_code == status.HTTP_200_OK
        
        # Check response data
        data = response.json()
        assert "message" in data
        assert "Authentication successful" in data["message"]
        # Check user data (matches actual response format)
        assert "email" in data
        assert data["email"] == "testuser1@example.com"
        assert "user_id" in data
    
    def test_protected_endpoint_no_auth(self, client):
        """Test accessing a protected endpoint without authentication"""
        response = client.get("/api/v1/auth/protected")
        
        # Check status code - should be unauthorized
        assert response.status_code == status.HTTP_401_UNAUTHORIZED or response.status_code == status.HTTP_403_FORBIDDEN
    
    @pytest.mark.skip(reason="Requires actual AWS Cognito integration")
    def test_register_cognito_user(self, client):
        """Test registering a new user via Cognito
        This test is marked as skip because it requires actual AWS Cognito integration
        """
        user_data = {
            "email": "newuser@example.com",
            "password": "StrongP@ssw0rd",
            "first_name": "New",
            "last_name": "User",
            "phone_number": "+1234567890"
        }
        
        response = client.post("/api/v1/auth/register", json=user_data)
        
        # Should be successful
        assert response.status_code == status.HTTP_201_CREATED
        
        data = response.json()
        assert data["email"] == user_data["email"]
        assert "id" in data
    
    @pytest.mark.skip(reason="Requires actual AWS Cognito integration")
    def test_register_duplicate_cognito_user(self, client, test_data):
        """Test registering a duplicate user
        This test is marked as skip because it requires actual AWS Cognito integration
        """
        # Try to register with an email that already exists
        user_data = {
            "email": test_data["users"][0].email,  # Using existing email
            "password": "StrongP@ssw0rd",
            "first_name": "Duplicate",
            "last_name": "User",
            "phone_number": "+0987654321"
        }
        
        response = client.post("/api/v1/auth/register", json=user_data)
        
        # Should be conflict error
        assert response.status_code == status.HTTP_409_CONFLICT