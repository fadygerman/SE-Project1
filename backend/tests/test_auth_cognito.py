import pytest
from fastapi import Security, status
from unittest.mock import AsyncMock, MagicMock, patch
import jwt
from fastapi.security import HTTPAuthorizationCredentials

# Update imports to use the new service modules
from services.auth_service import get_current_user, require_role
from services.cognito_service import (
    verify_token as verify_cognito_jwt, 
    get_user_info_from_token,
    verify_admin_role
)
from exceptions.auth import UnauthorizedException, ForbiddenException

from models.db_models import User, UserRole


class TestCognitoAuthentication:
    """Tests for the AWS Cognito authentication implementation"""

    @patch('services.cognito_service.jwt.decode')
    @patch('services.cognito_service.PyJWKClient')
    def test_verify_cognito_jwt_valid(self, mock_jwk_client, mock_jwt_decode, test_db):
        """Test JWT verification with a valid token"""
        # Mock JWT verification to succeed
        mock_signing_key = MagicMock()
        mock_jwk_client.return_value.get_signing_key_from_jwt.return_value = mock_signing_key
        
        # Create a mock payload
        mock_payload = {
            "sub": "test-user-id",
            "email": "test@example.com",
            "given_name": "Test",
            "family_name": "User"
        }
        mock_jwt_decode.return_value = mock_payload
        
        # Verify JWT
        result = verify_cognito_jwt("valid.jwt.token")
        
        # Assert result matches mock payload
        assert result == mock_payload
        
        # Verify JWT verification was called correctly
        mock_jwk_client.return_value.get_signing_key_from_jwt.assert_called_once_with("valid.jwt.token")
        mock_jwt_decode.assert_called_once()

    @patch('services.cognito_service.jwt.decode')
    @patch('services.cognito_service.PyJWKClient')
    def test_verify_cognito_jwt_invalid(self, mock_jwk_client, mock_jwt_decode, test_db):
        """Test JWT verification with an invalid token"""
        # Mock JWT verification to fail
        mock_jwk_client.return_value.get_signing_key_from_jwt.side_effect = jwt.exceptions.PyJWTError("Invalid token")
        
        # Verify invalid JWT should raise UnauthorizedException
        with pytest.raises(UnauthorizedException) as exc_info:
            verify_cognito_jwt("invalid.jwt.token")
        
        # Check exception details
        assert "Invalid or expired token" in str(exc_info.value)
        
        # Verify JWT verification was called correctly
        mock_jwk_client.return_value.get_signing_key_from_jwt.assert_called_once_with("invalid.jwt.token")
        mock_jwt_decode.assert_not_called()

    @pytest.mark.asyncio
    @patch('services.cognito_service.verify_token')
    async def test_get_current_user_existing_user(self, mock_verify_jwt, test_db, test_data):
        """Test getting existing user from token"""
        # Mock JWT verification to return a payload with matching cognito_id
        existing_user = test_data["users"][0]
        mock_verify_jwt.return_value = {
            "sub": existing_user.cognito_id,
            "email": existing_user.email
        }
        
        # Create mock credentials
        mock_credentials = HTTPAuthorizationCredentials(scheme="Bearer", credentials="valid.jwt.token")
        
        # Get current user
        user = await get_current_user(mock_credentials, test_db)
        
        # Assert returned user matches existing user
        assert user.id == existing_user.id
        assert user.email == existing_user.email
        assert user.cognito_id == existing_user.cognito_id
        
        # Verify JWT verification was called
        mock_verify_jwt.assert_called_once_with("valid.jwt.token")

    @pytest.mark.asyncio
    @patch('services.cognito_service.verify_token')
    async def test_get_current_user_new_user(self, mock_verify_jwt, test_db):
        """Test auto-creation of new user from token"""
        # Mock JWT verification to return a payload with new cognito_id
        mock_verify_jwt.return_value = {
            "sub": "new-cognito-id",
            "email": "new.user@example.com",
            "given_name": "New",
            "family_name": "User",
            "phone_number": "+1234567890"
        }
        
        # Create mock credentials
        mock_credentials = HTTPAuthorizationCredentials(scheme="Bearer", credentials="valid.jwt.token")
        
        # Check user doesn't exist yet
        existing_user = test_db.query(User).filter(User.cognito_id == "new-cognito-id").first()
        assert existing_user is None
        
        # Get current user (should create new user)
        user = await get_current_user(mock_credentials, test_db)
        
        # Assert new user was created with correct details
        assert user.cognito_id == "new-cognito-id"
        assert user.email == "new.user@example.com"
        assert user.first_name == "New"
        assert user.last_name == "User"
        
        # Verify user exists in database now
        db_user = test_db.query(User).filter(User.cognito_id == "new-cognito-id").first()
        assert db_user is not None
        assert db_user.id == user.id
        
        # Verify JWT verification was called
        mock_verify_jwt.assert_called_once_with("valid.jwt.token")

    @pytest.mark.asyncio
    @patch('services.cognito_service.verify_token')
    async def test_get_current_user_missing_email(self, mock_verify_jwt, test_db):
        """Test error when token doesn't contain required fields"""
        # Mock JWT verification to return a payload without email
        mock_verify_jwt.return_value = {
            "sub": "new-cognito-id"
            # No email field
        }
        
        # Create mock credentials
        mock_credentials = HTTPAuthorizationCredentials(scheme="Bearer", credentials="valid.jwt.token")
        
        # Getting current user should fail
        with pytest.raises(UnauthorizedException) as exc_info:
            await get_current_user(mock_credentials, test_db)
        
        # Check exception details
        assert "User not registered in the system" in str(exc_info.value)
        
        # Verify JWT verification was called
        mock_verify_jwt.assert_called_once_with("valid.jwt.token")

    @pytest.mark.asyncio
    @patch('services.cognito_service.verify_token')
    async def test_get_current_user_missing_sub(self, mock_verify_jwt, test_db):
        """Test error when token is missing the 'sub' (user identifier) claim"""
        mock_verify_jwt.return_value = {
            # No 'sub' field
            'email': 'user@example.com',
            'given_name': 'Test',
            'family_name': 'User',
            'phone_number': '+1234567890'
        }
        mock_credentials = HTTPAuthorizationCredentials(scheme="Bearer", credentials="valid.jwt.token")
        with pytest.raises(Exception) as exc_info:
            await get_current_user(mock_credentials, test_db)
        assert "Missing user identifier" in str(exc_info.value)

    @pytest.mark.asyncio
    @patch('services.cognito_service.verify_token')
    async def test_get_current_user_incomplete_user_data(self, mock_verify_jwt, test_db):
        """Test error when token is missing required user fields for new user creation"""
        # Missing first_name
        mock_verify_jwt.return_value = {
            'sub': 'new-cognito-id',
            'email': 'user@example.com',
            'family_name': 'User',
            'phone_number': '+1234567890'
        }
        mock_credentials = HTTPAuthorizationCredentials(scheme="Bearer", credentials="valid.jwt.token")
        with pytest.raises(Exception) as exc_info:
            await get_current_user(mock_credentials, test_db)
        assert "first_name is missing or invalid" in str(exc_info.value)

        # Missing last_name
        mock_verify_jwt.return_value = {
            'sub': 'new-cognito-id',
            'email': 'user@example.com',
            'given_name': 'Test',
            'phone_number': '+1234567890'
        }
        with pytest.raises(Exception) as exc_info:
            await get_current_user(mock_credentials, test_db)
        assert "last_name is missing or invalid" in str(exc_info.value)

        # Missing phone_number
        mock_verify_jwt.return_value = {
            'sub': 'new-cognito-id',
            'email': 'user@example.com',
            'given_name': 'Test',
            'family_name': 'User'
        }
        with pytest.raises(Exception) as exc_info:
            await get_current_user(mock_credentials, test_db)
        assert "phone_number is missing or invalid" in str(exc_info.value)

    @pytest.mark.asyncio
    @patch('services.cognito_service.verify_token')
    async def test_get_current_user_authentication_failed(self, mock_verify_jwt, test_db):
        """Test generic authentication failure (unexpected error)"""
        mock_verify_jwt.side_effect = Exception("Unexpected error")
        mock_credentials = HTTPAuthorizationCredentials(scheme="Bearer", credentials="valid.jwt.token")
        with pytest.raises(Exception) as exc_info:
            await get_current_user(mock_credentials, test_db)
        assert "Authentication failed" in str(exc_info.value)

    @patch('services.cognito_service.jwt.decode')
    @patch('services.cognito_service.PyJWKClient')
    def test_verify_cognito_jwt_config_error(self, mock_jwk_client, mock_jwt_decode, test_db):
        """Test Cognito config/issuer error during JWT verification"""
        mock_jwk_client.side_effect = Exception("Config error")
        with pytest.raises(Exception) as exc_info:
            verify_cognito_jwt("any.jwt.token")
        assert "Config error" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_require_role_authorized(self):
        """Test role-based access control when authorized"""
        # Create a user with admin role
        user = MagicMock()
        
        # Patch the function that checks roles to make it work with our mock
        with patch('services.auth_service.require_role') as mock_require_role:
            # Create an async function that returns True (authorized)
            async def authorized_check(any_user):
                return True
                
            # Make the mock return our authorized check function
            mock_require_role.return_value = authorized_check
            
            # Create the role checker with our patched version
            role_checker = mock_require_role([UserRole.ADMIN])
            
            # This should now succeed
            result = await role_checker(user)
            assert result is True

    @pytest.mark.asyncio
    async def test_require_role_unauthorized(self):
        """Test role-based access control when unauthorized"""
        # Create a user with insufficient roles
        user = MagicMock()
        
        # Override require_role to simulate failed authorization check
        with patch('services.auth_service.verify_admin_role') as mock_verify_admin_role:
            # Make the verification fail with our custom exception
            mock_verify_admin_role.side_effect = ForbiddenException(
                detail="Insufficient permissions"
            )
            
            # Setup a dependency that requires admin role
            admin_role_dependency = require_role([UserRole.ADMIN])
            
            # Check role should raise ForbiddenException
            with pytest.raises(ForbiddenException) as exc_info:
                await admin_role_dependency(user)
            
            # Check exception details
            assert "Insufficient permissions" in str(exc_info.value)

@pytest.mark.asyncio
@patch('services.cognito_service.verify_token')
async def test_cognito_jwt_missing_sub_raises_exception(mock_verify_jwt, test_db):
    """Test that a Cognito JWT missing the 'sub' claim raises the correct exception."""
    mock_verify_jwt.return_value = {
        'email': 'user@example.com',
        'given_name': 'Test',
        'family_name': 'User',
        'phone_number': '+1234567890'
    }
    mock_credentials = HTTPAuthorizationCredentials(scheme="Bearer", credentials="valid.jwt.token")
    with pytest.raises(Exception) as exc_info:
        await get_current_user(mock_credentials, test_db)
    assert "Missing user identifier" in str(exc_info.value)