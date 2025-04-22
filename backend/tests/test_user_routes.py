import pytest
from fastapi import status

from main import app


class TestUserRetrieval:
    """Tests related to retrieving users"""
    
    def test_get_all_users(self, admin_client, test_data):
        """Test getting all users"""
        response = admin_client.get("/api/v1/users/")
        
        # Check status code
        assert response.status_code == status.HTTP_200_OK
        
        # Check response data
        users = response.json()
        assert len(users) == 2
        assert users[0]["email"] == "testuser1@example.com"
        assert users[1]["email"] == "testuser2@example.com"

    def test_get_user_by_id(self, auth_client, test_data):
        """Test getting a user by ID"""
        user_id = test_data["users"][0].id
        
        response = auth_client.get(f"/api/v1/users/{user_id}")
        
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
        
    def test_get_user_by_id_unauthorized(self, auth_client, test_data):
        """Test getting another user's data (should be forbidden)"""
        # Create a fixture that authenticates as user 2
        async def override_get_current_user():
            return test_data["users"][1]
        
        # Store original overrides
        original_overrides = app.dependency_overrides.copy()
        
        # Set the test user to user 2
        from services.auth_service import get_current_user
        app.dependency_overrides[get_current_user] = override_get_current_user
        
        try:
            # Try to access user 1's data as user 2
            user_id = test_data["users"][0].id
            response = auth_client.get(f"/api/v1/users/{user_id}")
            
            # Check status code - should be forbidden
            assert response.status_code == status.HTTP_403_FORBIDDEN
            
            # Check error message
            error = response.json()
            assert "detail" in error
            assert "You can only access your own user data" in error["detail"]
        finally:
            # Restore original overrides
            app.dependency_overrides = original_overrides

    def test_get_user_not_found(self, auth_client, test_data):
        """Test getting a non-existent user"""
        non_existent_id = 999
        
        # Create a custom override to simulate a self-access attempt for a non-existent user
        async def override_get_current_user():
            user = test_data["users"][0]
            user.id = non_existent_id  # Modify the user ID to match the requested ID
            return user
            
        # Store original overrides
        original_overrides = app.dependency_overrides.copy()
        
        # Apply our custom override
        from services.auth_service import get_current_user
        app.dependency_overrides[get_current_user] = override_get_current_user
        
        try:
            response = auth_client.get(f"/api/v1/users/{non_existent_id}")
            
            # Check status code
            assert response.status_code == status.HTTP_404_NOT_FOUND
            
            # Check error message
            error = response.json()
            assert "detail" in error
            assert f"User with ID {non_existent_id} not found" in error["detail"]
        finally:
            # Restore original overrides
            app.dependency_overrides = original_overrides
        
    def test_get_current_user_profile(self, auth_client, test_data):
        """Test getting the current user's profile"""
        response = auth_client.get("/api/v1/users/me/profile")
        
        # Check status code
        assert response.status_code == status.HTTP_200_OK
        
        # Check that the correct user data is returned
        user = response.json()
        assert user["id"] == test_data["users"][0].id
        assert user["email"] == "testuser1@example.com"
        assert user["cognito_id"] == "cognito1"
