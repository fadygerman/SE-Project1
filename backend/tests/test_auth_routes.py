import asyncio
import unittest.mock as mock

import jwt
import pytest
from fastapi import HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials
from fastapi.testclient import TestClient

from exceptions.auth import InvalidTokenException
from main import app
from services.auth_service import get_current_user
from services.cognito_service import verify_cognito_jwt

client = TestClient(app)

class TestAuthRoutes:
    """Tests related to authentication routes"""
    
    def test_public_endpoint(self, auth_client):
        """Test accessing a public endpoint"""
        response = auth_client.get("/api/v1/auth/public")
        
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

    def test_protected_route_requires_auth(self, client):
        """Test that accessing a protected route without a token returns an auth error."""
        response = client.get("/api/v1/users/me/profile")
        
        # Accept either 401 or 403 as both indicate authentication/authorization failure
        assert response.status_code in [401, 403]
        assert any(text in response.text.lower() for text in ["not authenticated", "unauthorized", "forbidden"])

class TestAuthEdgeCases:
    """Tests for edge cases and error handling in authentication system"""
    
    @pytest.mark.asyncio
    @mock.patch('services.auth_service.logger')
    @mock.patch('services.auth_service.verify_cognito_jwt')
    async def test_db_error_during_user_retrieval(self, mock_verify_jwt, mock_logger, test_db):
        """Test handling of database error during user retrieval"""
        # Arrange: Mock JWT validation to return valid token payload
        mock_verify_jwt.return_value = {
            "sub": "test-cognito-id",
            "email": "test@example.com"
        }
        db_error_message = "Database connection error"
    
        # Mock database session to raise exception during query
        with mock.patch('sqlalchemy.orm.Session.query') as mock_query:
            mock_query.side_effect = Exception(db_error_message)
            credentials = HTTPAuthorizationCredentials(scheme="Bearer", credentials="test-token")

            # Expect HTTPException 500
            with pytest.raises(HTTPException) as excinfo:
                await get_current_user(credentials, test_db)

            # Assert status code 500 and detail
            assert excinfo.value.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
            assert "An internal error occurred during authentication." in excinfo.value.detail

            # Assert logger was called
            mock_logger.error.assert_called_once()
            args, kwargs = mock_logger.error.call_args
            assert "Unexpected error during user authentication/creation" in args[0]
            assert db_error_message in str(args[1])
            assert kwargs.get('exc_info') is True
    
    @pytest.mark.parametrize("jwt_error, expected_message", [
        (jwt.ExpiredSignatureError("Token expired"), "Invalid or expired token"),
        (jwt.InvalidTokenError("Invalid token"), "Invalid or expired token"),
        (jwt.InvalidSignatureError("Invalid signature"), "Invalid or expired token"),
        (jwt.DecodeError("Decode error"), "Invalid or expired token"),
    ])
    @mock.patch('services.cognito_service.PyJWKClient')
    def test_jwt_validation_errors(self, mock_jwk_client, jwt_error, expected_message, test_db):
        """Test handling of various JWT validation errors"""
        # Arrange: Mock JWT validation to raise specific exception
        mock_jwk_client.return_value.get_signing_key_from_jwt.side_effect = jwt_error
        
        # Act & Assert
        with pytest.raises(InvalidTokenException) as excinfo:
            verify_cognito_jwt("invalid-token")
        
        assert expected_message in str(excinfo.value)
    
    @mock.patch('services.auth_service.verify_cognito_jwt')
    def test_malformed_token(self, mock_verify_jwt, client):
        """Test handling of malformed token"""
        # Arrange: Configure mock to raise InvalidTokenException for the specific token
        mock_verify_jwt.side_effect = InvalidTokenException

        # Act: Send request with the token that triggers the exception
        response = client.get(
            "/api/v1/users/me/profile", # Or any other protected route
            headers={"Authorization": "Bearer malformed.token.here"}
        )
        
        # Assert: Should return 401 Unauthorized
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        # Optionally check the detail message if needed
        assert "Invalid or expired token" in response.json().get("detail", "")
        # Ensure the mock was called with the specific token
        mock_verify_jwt.assert_called_with("malformed.token.here")
        
    @mock.patch('services.auth_service.verify_cognito_jwt')
    def test_create_user_with_minimal_valid_data(self, mock_verify_jwt, test_db):
        """Test user creation with minimal valid data from token"""
        # Arrange: Mock JWT validation to return minimal valid data
        cognito_id = "minimal-data-user"
        mock_verify_jwt.return_value = {
            "sub": cognito_id,
            "email": "minimal@example.com",
            "name": "User",  # Minimal valid first name
            "family_name": "Profile",  # Minimal valid last name
            "phone_number": "+1234567890"  # Valid phone number
        }
        
        # Create fake credentials
        credentials = HTTPAuthorizationCredentials(scheme="Bearer", credentials="test-token")
        
        # Act: Get current user (should create new user with minimal data)
        user = asyncio.run(get_current_user(credentials, test_db))
        
        # Assert: User should be created with correct data
        assert user.cognito_id == cognito_id
        assert user.email == "minimal@example.com"
        assert user.first_name == "User"
        assert user.last_name == "Profile"
        
        # Clean up - remove test user
        test_db.delete(user)
        test_db.commit()