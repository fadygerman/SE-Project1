import pytest
from fastapi import status

class TestUserRetrieval:
    """Tests related to retrieving users"""
    
    def test_get_all_users(self, client, test_data):
        """Test getting all users"""
        response = client.get("/api/v1/users/")
        
        # Check status code
        assert response.status_code == status.HTTP_200_OK
        
        # Check response data
        users = response.json()
        assert len(users) == 2
        assert users[0]["email"] == "testuser1@example.com"
        assert users[1]["email"] == "testuser2@example.com"

    def test_get_user_by_id(self, client, test_data):
        """Test getting a user by ID"""
        user_id = test_data["users"][0].id
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
        
        # Password hash should be excluded
        assert "password_hash" not in user

    def test_get_user_not_found(self, client, test_data):
        """Test getting a non-existent user"""
        non_existent_id = 999
        response = client.get(f"/api/v1/users/{non_existent_id}")
        
        # Check status code
        assert response.status_code == status.HTTP_404_NOT_FOUND
        
        # Check error message
        error = response.json()
        assert "detail" in error
        assert f"User with ID {non_existent_id} not found" in error["detail"]
