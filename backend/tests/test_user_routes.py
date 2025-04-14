import pytest
from fastapi import status
from unittest import mock
from utils.auth_cognito import get_current_user

@mock.patch('utils.auth_cognito.get_current_user')
class TestUserRetrieval:
    """Tests related to retrieving users"""
    
    def test_get_all_users(self, mock_auth, client, test_data):
        """Test getting all users"""
        # Mock authentication with admin privileges
        mock_auth.return_value = test_data["users"][0]
        
        response = client.get("/api/v1/users/")
        
        # Check status code
        assert response.status_code == status.HTTP_200_OK
        
        # Check response data
        users = response.json()
        assert len(users) == 2
        assert users[0]["email"] == "testuser1@example.com"
        assert users[1]["email"] == "testuser2@example.com"

    def test_get_user_by_id(self, mock_auth, client, test_data):
        """Test getting a user by ID"""
        user_id = test_data["users"][0].id
        
        # Mock authentication as the user being requested (self-access)
        mock_auth.return_value = test_data["users"][0]
        
        response = client.get(f"/api/v1/users/{user_id}")
        
        # Check status code
        assert response.status_code == status.HTTP_200_OK
        
        # Check response data
        user = response.json()
        assert user["id"] == user_id
        assert user["email"] == "testuser1@example.com"
        assert user["first_name"] == "Test"
        assert user["last_name"] == "User1"
        assert user["phone_number"] == "+1234567890"
        assert user["cognito_id"] == "cognito1"
        
    def test_get_user_by_id_unauthorized(self, mock_auth, client, test_data):
        """Test getting another user's data (should be forbidden)"""
        # User 2 trying to access User 1's data
        user_id = test_data["users"][0].id
        mock_auth.return_value = test_data["users"][1]
        
        response = client.get(f"/api/v1/users/{user_id}")
        
        # Check status code - should be forbidden
        assert response.status_code == status.HTTP_403_FORBIDDEN
        
        # Check error message
        error = response.json()
        assert "detail" in error
        assert "You can only access your own user data" in error["detail"]

    def test_get_user_not_found(self, mock_auth, client, test_data):
        """Test getting a non-existent user"""
        non_existent_id = 999
        
        # Mock authentication as admin user
        mock_auth.return_value = test_data["users"][0]
        mock_auth.return_value.id = non_existent_id  # Make it look like self-access
        
        response = client.get(f"/api/v1/users/{non_existent_id}")
        
        # Check status code
        assert response.status_code == status.HTTP_404_NOT_FOUND
        
        # Check error message
        error = response.json()
        assert "detail" in error
        assert f"User with ID {non_existent_id} not found" in error["detail"]
        
    def test_get_current_user_profile(self, mock_auth, client, test_data):
        """Test getting the current user's profile"""
        # Mock authentication
        mock_auth.return_value = test_data["users"][0]
        
        response = client.get("/api/v1/users/me/profile")
        
        # Check status code
        assert response.status_code == status.HTTP_200_OK
        
        # Check that the correct user data is returned
        user = response.json()
        assert user["id"] == test_data["users"][0].id
        assert user["email"] == "testuser1@example.com"
        assert user["cognito_id"] == "cognito1"
