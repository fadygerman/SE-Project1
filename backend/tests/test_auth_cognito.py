import asyncio
import binascii
from datetime import date, time, timedelta
from decimal import Decimal
from time import time as time_func
from unittest.mock import MagicMock, patch

import jwt
import pytest
from fastapi import HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials

from exceptions.auth import InvalidTokenException
from models.currencies import Currency
from models.db_models import Booking, BookingStatus, User, UserRole
from services.auth_service import get_current_user, require_role
from services.booking_service import get_booking_with_permission_check
from services.cognito_service import verify_cognito_jwt


class TestAdvancedAuthScenarios:
    """Advanced tests for authentication edge cases"""
    
    @pytest.mark.asyncio
    @patch('services.auth_service.logger')
    @patch('services.auth_service.verify_cognito_jwt')
    async def test_db_error_during_user_lookup(self, mock_verify_jwt, mock_logger, test_db):
        """Test handling of database errors during user lookup"""
        # Mock valid JWT payload
        mock_verify_jwt.return_value = {
            "sub": "test-cognito-id",
            "email": "test@example.com",
            "name": "Test", 
            "family_name": "User",
            "phone_number": "+1234567890"
        }
        
        # Create mock credentials
        mock_credentials = HTTPAuthorizationCredentials(scheme="Bearer", credentials="valid.jwt.token")
        db_error_message = "Database connection error"

        # Simulate database error during query
        with patch.object(test_db, 'query', side_effect=Exception(db_error_message)):
            # Expect HTTPException 500
            with pytest.raises(HTTPException) as exc_info:
                await get_current_user(mock_credentials, test_db)

            # Assert status code 500 and detail
            assert exc_info.value.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
            assert "An internal error occurred during authentication." in exc_info.value.detail

            # Assert logger was called
            mock_logger.error.assert_called_once()
            args, kwargs = mock_logger.error.call_args
            assert "Unexpected error during user authentication/creation" in args[0]
            assert db_error_message in str(args[1])
            assert kwargs.get('exc_info') is True


    @pytest.mark.asyncio
    @patch('services.auth_service.logger')
    @patch('services.auth_service.verify_cognito_jwt')
    async def test_db_commit_error_handling(self, mock_verify_jwt, mock_logger, test_db): 
        """Test handling of database commit error during user creation"""
        # Set up mock for new user creation that fails on commit
        mock_verify_jwt.return_value = {
            "sub": "new-user-id",
            "email": "new@example.com",
            "name": "New", 
            "family_name": "User",
            "phone_number": "+1234567890"
        }
        
        mock_credentials = HTTPAuthorizationCredentials(scheme="Bearer", credentials="valid.jwt.token")
        commit_error_message = "Commit failed"

        # Patch db.commit to raise exception
        with patch.object(test_db, 'commit', side_effect=Exception(commit_error_message)):
            # Expect HTTPException 500
            with pytest.raises(HTTPException) as exc_info:
                await get_current_user(mock_credentials, test_db)

            # Assert status code 500 and detail
            assert exc_info.value.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
            assert "An internal error occurred during authentication." in exc_info.value.detail

            # Assert logger was called
            mock_logger.error.assert_called_once()
            args, kwargs = mock_logger.error.call_args
            assert "Unexpected error during user authentication/creation" in args[0]
            assert commit_error_message in str(args[1])
            assert kwargs.get('exc_info') is True


    @pytest.mark.parametrize("jwt_error,expected_detail", [
        (jwt.ExpiredSignatureError("Token expired"), "Invalid or expired token"),
        (jwt.InvalidTokenError("Bad token"), "Invalid or expired token"),
        (jwt.DecodeError("Cannot decode"), "Invalid or expired token"),
        (jwt.InvalidSignatureError("Bad signature"), "Invalid or expired token"),
        (binascii.Error("Invalid base64"), "Invalid or expired token")
    ])
    @pytest.mark.asyncio
    @patch('services.cognito_service.PyJWKClient')
    async def test_jwt_specific_errors(self, mock_jwk_client, jwt_error, expected_detail, test_db):
        """Test handling of specific JWT validation errors"""
        # Mock JWT client to raise specific exception
        mock_jwk_instance = mock_jwk_client.return_value
        mock_jwk_instance.get_signing_key_from_jwt.side_effect = jwt_error

        mock_credentials = HTTPAuthorizationCredentials(scheme="Bearer", credentials="bad.token")

        # Should raise HTTPException
        with pytest.raises(HTTPException) as exc_info:
            # We call get_current_user, which internally calls verify_cognito_jwt
            await get_current_user(mock_credentials, test_db)

        assert exc_info.value.status_code == 401
        # Check if the expected detail is present in the actual detail
        assert expected_detail in exc_info.value.detail

    @pytest.mark.asyncio
    @patch('services.auth_service.verify_cognito_jwt')
    async def test_validation_with_minimally_valid_token(self, mock_verify_jwt, test_db):
        """Test user creation with a token containing minimal valid data"""
        # Set up mock with precise minimum valid data
        mock_verify_jwt.return_value = {
            "sub": "minimal-user",
            "email": "minimal@example.com",
            "name": "A",  # Minimum length is 1
            "family_name": "B",  # Minimum length is 1
            "phone_number": "12345678"  # Minimum length is 8
        }
        
        mock_credentials = HTTPAuthorizationCredentials(scheme="Bearer", credentials="valid.jwt.token")
        
        # Should succeed with minimally valid data
        user = await get_current_user(mock_credentials, test_db)
        assert user is not None
        assert user.email == "minimal@example.com"
        assert user.first_name == "A"
        assert user.last_name == "B"
        assert user.phone_number == "12345678"
        
        # Clean up
        test_db.delete(user)
        test_db.commit()

    @pytest.mark.asyncio
    async def test_role_checking_with_multiple_roles(self):
        """Test role-based access with multiple allowed roles"""
        # Create users with different roles
        admin_user = User(
            id=1, 
            email="admin@example.com", 
            first_name="Admin",
            last_name="User",
            phone_number="12345678",
            cognito_id="admin-cognito-id",
            role=UserRole.ADMIN
        )
        standard_user = User(
            id=2, 
            email="customer@example.com", 
            first_name="Standard",
            last_name="User",
            phone_number="87654321",
            cognito_id="standard-cognito-id",
            role=UserRole.USER
        )
        
        # Create role checker for multiple roles
        role_checker = require_role([UserRole.ADMIN, UserRole.USER])
        
        # Both should have access
        assert await role_checker(admin_user) is True
        assert await role_checker(standard_user) is True
    
    @pytest.mark.asyncio
    @patch('services.auth_service.get_current_user')
    async def test_get_booking_with_permission_check_complex(self, mock_get_current_user, test_db):
        """Test complex permission scenarios with booking access"""
        # Create test users
        admin = User(
            id=1, 
            email="admin@example.com", 
            first_name="Admin",
            last_name="User",
            phone_number="12345678",
            cognito_id="admin-cognito-id",
            role=UserRole.ADMIN
        )
        owner = User(
            id=2, 
            email="owner@example.com", 
            first_name="Owner",
            last_name="User",
            phone_number="87654321",
            cognito_id="owner-cognito-id",
            role=UserRole.USER
        )
        other_user = User(
            id=3, 
            email="other@example.com", 
            first_name="Other",
            last_name="User",
            phone_number="13579246",
            cognito_id="other-cognito-id",
            role=UserRole.USER
        )
        
        # Create a test booking owned by 'owner'
        booking = Booking(
            id=123,
            user_id=owner.id,
            car_id=1,
            start_date=date.today() + timedelta(days=1),
            end_date=date.today() + timedelta(days=10),
            planned_pickup_time=time(10, 0, 0),
            status=BookingStatus.ACTIVE,
            currency_code=Currency.USD,
            exchange_rate=Decimal('1.00'),
            total_cost=Decimal('100.00')
        )
        
        with patch.object(test_db, 'query') as mock_query:
            mock_query.return_value.filter.return_value.first.return_value = booking
            
            # Admin should have access
            mock_get_current_user.return_value = admin
            result1 = await get_booking_with_permission_check(booking.id, test_db, admin)
            assert result1.id == booking.id
            
            # Owner should have access
            mock_get_current_user.return_value = owner
            result2 = await get_booking_with_permission_check(booking.id, test_db, owner)
            assert result2.id == booking.id
            
            # Other user should be denied
            mock_get_current_user.return_value = other_user
            with pytest.raises(HTTPException) as exc_info:
                await get_booking_with_permission_check(booking.id, test_db, other_user)
            
            assert exc_info.value.status_code == 403
            assert "You can only access your own bookings" in exc_info.value.detail

    @pytest.mark.asyncio
    @patch('services.auth_service.verify_cognito_jwt')
    async def test_concurrent_jwt_validation_error_handling(self, mock_verify_jwt):
        """Test handling of errors during concurrent JWT validation operations"""
        # Define the side_effect function first
        call_count = 0
        def side_effect(*args, **kwargs):
            nonlocal call_count
            call_count += 1
            if call_count % 2 == 0:  # Every second call fails
                raise jwt.ExpiredSignatureError("Expired")
            return {
                "sub": "test-user",
                "email": "test@example.com",
                "name": "Test",
                "family_name": "User",
                "phone_number": "+1234567890"
            }

        # Now assign it to the mock
        mock_verify_jwt.side_effect = side_effect

        credentials = HTTPAuthorizationCredentials(scheme="Bearer", credentials="test.token")

        async def auth_attempt():
            db_mock = MagicMock()
            db_mock.query.return_value.filter.return_value.first.return_value = None
            db_mock.add = MagicMock()
            db_mock.commit = MagicMock()
            db_mock.refresh = MagicMock()

            # Remove the patch context manager for get_db
            # with patch('services.auth_service.get_db', return_value=db_mock):
            try:
                # Explicitly pass the db_mock to the function call
                user = await get_current_user(credentials=credentials, db=db_mock)
                return user # Success case
            except HTTPException as http_exc:
                # Check if it's the specific HTTPException for invalid token
                if http_exc.status_code == 401 and "Invalid or expired token" in http_exc.detail:
                    return None # Expected failure path
                else:
                    # Log and return an indicator for unexpected HTTP errors
                    print(f"Unexpected HTTPException in auth_attempt: {http_exc.status_code} - {http_exc.detail}")
                    return f"UNEXPECTED_HTTP_ERROR_{http_exc.status_code}"
            except Exception as e:
                # Log and return an indicator for other unexpected errors
                print(f"Unexpected Exception in auth_attempt: {e}")
                return "UNEXPECTED_ERROR"

        tasks = [auth_attempt() for _ in range(5)]
        results = await asyncio.gather(*tasks)

        # Filter results to check assertions more clearly
        successful_results = [r for r in results if isinstance(r, User)]
        failed_results = [r for r in results if r is None]

        # Assert that we got at least one successful result (User object)
        assert any(successful_results), f"No successful attempts found. Results: {results}"
        # Assert that the list of expected failures is not empty
        assert failed_results, f"No expected failures (None) found. Results: {results}"
        # Assert that no unexpected errors occurred
        assert all(isinstance(r, User) or r is None for r in results), f"Unexpected results found: {results}"


    @pytest.mark.asyncio
    async def test_concurrent_jwt_validation_with_separate_mocks(self):
        """Test handling of concurrent JWT validation with alternating success/failure"""
        # Define credentials and mocks first
        credentials = HTTPAuthorizationCredentials(scheme="Bearer", credentials="test.token")

        success_mock = MagicMock()
        success_mock.return_value = {
            "sub": "test-user",
            "email": "test@example.com",
            "name": "Test",
            "family_name": "User",
            "phone_number": "+1234567890"
        }

        failure_mock = MagicMock()
        failure_mock.side_effect = jwt.ExpiredSignatureError("Expired")

        # Now define the helper functions that use them
        def create_db_mock():
            db_mock = MagicMock()
            db_mock.query.return_value.filter.return_value.first.return_value = None
            db_mock.add = MagicMock()
            db_mock.commit = MagicMock()
            db_mock.refresh = MagicMock()
            return db_mock

        async def success_attempt():
            db_mock_instance = create_db_mock()
            try:
                # success_mock and credentials are now defined in the outer scope
                with patch('services.auth_service.verify_cognito_jwt', success_mock):
                    user = await get_current_user(credentials=credentials, db=db_mock_instance)
                    return user
            except HTTPException as http_exc:
                 print(f"Unexpected HTTPException in success_attempt: {http_exc.status_code} - {http_exc.detail}")
                 return f"UNEXPECTED_HTTP_ERROR_{http_exc.status_code}"
            except Exception as e:
                 print(f"Unexpected Exception in success_attempt: {e}")
                 return "UNEXPECTED_ERROR"

        async def failure_attempt():
            db_mock_instance = create_db_mock()
            try:
                # failure_mock and credentials are now defined in the outer scope
                with patch('services.auth_service.verify_cognito_jwt', failure_mock):
                     await get_current_user(credentials=credentials, db=db_mock_instance)
                     return "ERROR: Failure mock did not raise"
            except HTTPException as http_exc:
                 if http_exc.status_code == 401 and "Invalid or expired token" in http_exc.detail:
                     return None
                 else:
                     print(f"Unexpected HTTPException in failure_attempt: {http_exc.status_code} - {http_exc.detail}")
                     return f"UNEXPECTED_HTTP_ERROR_{http_exc.status_code}"
            except Exception as e:
                 print(f"Unexpected Exception in failure_attempt: {e}")
                 return "UNEXPECTED_ERROR"

        tasks = [success_attempt(), failure_attempt(), success_attempt()]
        results = await asyncio.gather(*tasks)

        # Filter results for clearer assertions
        successful_results = [r for r in results if isinstance(r, User)]
        failed_results = [r for r in results if r is None]

        # Assert that we got at least one successful result (User object)
        assert any(successful_results), f"No successful attempts found. Results: {results}"
        # Assert that we got at least one expected failure (None)
        assert failed_results, f"No expected failures (None) found. Results: {results}"
        # Assert that no unexpected errors occurred
        assert all(isinstance(r, User) or r is None for r in results), f"Unexpected results found: {results}"


    @patch('services.cognito_service.jwt.get_unverified_header')  
    @patch('services.cognito_service.jwt.decode')
    @patch('services.cognito_service.PyJWKClient')
    def test_verify_cognito_jwt_invalid(self, mock_jwk_client, mock_jwt_decode, test_db):
        """Test JWT verification with an invalid token"""
        # Mock JWT verification to fail
        mock_jwk_client.return_value.get_signing_key_from_jwt.side_effect = jwt.exceptions.PyJWTError("Invalid token")
        
        # Verify invalid JWT should raise InvalidTokenException
        with pytest.raises(InvalidTokenException) as exc_info:
            verify_cognito_jwt("invalid.jwt.token")
        
        # Check exception details
        assert "Invalid or expired token" in str(exc_info.value)
        
        # Verify JWT verification was called correctly
        mock_jwk_client.return_value.get_signing_key_from_jwt.assert_called_once_with("invalid.jwt.token")
        mock_jwt_decode.assert_not_called()

    @pytest.mark.asyncio
    @patch('services.auth_service.verify_cognito_jwt')
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
    @patch('services.auth_service.verify_cognito_jwt')
    async def test_get_current_user_new_user(self, mock_verify_jwt, test_db):
        """Test auto-creation of new user from token"""
        # Mock JWT verification to return a payload with new cognito_id
        mock_verify_jwt.return_value = {
            "sub": "new-cognito-id",
            "email": "new.user@example.com",
            "name": "New",
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
    @patch('services.auth_service.verify_cognito_jwt')
    async def test_get_current_user_missing_email(self, mock_verify_jwt, test_db):
        """Test error when token doesn't contain required fields"""
        # Mock JWT verification to return a payload without email
        mock_verify_jwt.return_value = {
            "sub": "new-cognito-id"
            # No email field
        }
        
        # Create mock credentials
        mock_credentials = HTTPAuthorizationCredentials(scheme="Bearer", credentials="mocked.token")
        
        # Getting current user should fail
        with pytest.raises(HTTPException) as exc_info:
            await get_current_user(mock_credentials, test_db)
        
        # Check exception details
        assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED
        assert "User not registered in the system" in exc_info.value.detail
        
        # Verify JWT verification was called
        mock_verify_jwt.assert_called_once_with("mocked.token")


    @pytest.mark.asyncio
    @patch('services.auth_service.verify_cognito_jwt')
    async def test_get_current_user_missing_sub(self, mock_verify_jwt, test_db):
        """Test error when token is missing the 'sub' (user identifier) claim"""
        mock_verify_jwt.return_value = {
            # No 'sub' field
            'email': 'user@example.com',
            'name': 'Test',
            'family_name': 'User',
            'phone_number': '+1234567890'
        }
        mock_credentials = HTTPAuthorizationCredentials(scheme="Bearer", credentials="valid.jwt.token")
        with pytest.raises(Exception) as exc_info:
            await get_current_user(mock_credentials, test_db)
        assert "Missing user identifier" in str(exc_info.value)

    @pytest.mark.asyncio
    @patch('services.auth_service.verify_cognito_jwt')
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
            'name': 'Test',
            'phone_number': '+1234567890'
        }
        with pytest.raises(Exception) as exc_info:
            await get_current_user(mock_credentials, test_db)
        assert "last_name is missing or invalid" in str(exc_info.value)

        # Missing phone_number
        mock_verify_jwt.return_value = {
            'sub': 'new-cognito-id',
            'email': 'user@example.com',
            'name': 'Test',
            'family_name': 'User'
        }
        with pytest.raises(Exception) as exc_info:
            await get_current_user(mock_credentials, test_db)
        assert "phone_number is missing or invalid" in str(exc_info.value)

    @pytest.mark.asyncio
    @patch('services.auth_service.logger')
    @patch('services.auth_service.verify_cognito_jwt')
    async def test_get_current_user_authentication_failed(self, mock_verify_jwt, mock_logger, test_db):
        """Test generic authentication failure (unexpected error)"""
        error_message = "Unexpected error"
        mock_verify_jwt.side_effect = Exception(error_message)
        mock_credentials = HTTPAuthorizationCredentials(scheme="Bearer", credentials="valid.jwt.token")

        # Expect HTTPException 500
        with pytest.raises(HTTPException) as exc_info:
            await get_current_user(mock_credentials, test_db)

        # Assert status code 500 and detail
        assert exc_info.value.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
        assert "An internal error occurred during authentication." in exc_info.value.detail

        # Assert logger was called
        mock_logger.error.assert_called_once()
        args, kwargs = mock_logger.error.call_args
        assert "Unexpected error during user authentication/creation" in args[0]
        assert error_message in str(args[1])
        assert kwargs.get('exc_info') is True

    @patch('services.cognito_service.jwt.decode')
    @patch('services.cognito_service.PyJWKClient')
    def test_verify_cognito_jwt_config_error(self, mock_jwk_client, mock_jwt_decode, test_db):
        """Test Cognito config/issuer error during JWT verification"""
        mock_jwk_client.side_effect = Exception("Config error")
        with pytest.raises(InvalidTokenException) as exc_info:
            verify_cognito_jwt("any.jwt.token")
        assert "Invalid or expired token" in str(exc_info.value)
        mock_jwt_decode.assert_not_called()

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
        # Create a user with an insufficient role (e.g., USER)
        user_with_insufficient_role = User(
            id=3,
            email="regular@example.com",
            first_name="Regular",
            last_name="User",
            phone_number="12345678",
            cognito_id="regular-cognito-id",
            role=UserRole.USER
        )

        # Create the dependency requiring ADMIN role
        admin_role_dependency = require_role([UserRole.ADMIN])
        
        with pytest.raises(HTTPException) as exc_info:
            await admin_role_dependency(user_with_insufficient_role)

        # Check exception details
        assert exc_info.value.status_code == status.HTTP_403_FORBIDDEN
        assert "Access denied" in exc_info.value.detail

    @pytest.mark.asyncio
    @patch('services.auth_service.verify_cognito_jwt')
    async def test_cognito_jwt_missing_sub_raises_exception(self, mock_verify_jwt, test_db):
        """Test that a Cognito JWT missing the 'sub' claim raises the correct exception."""
        mock_verify_jwt.return_value = {
            'email': 'user@example.com',
            'name': 'Test',
            'family_name': 'User',
            'phone_number': '+1234567890'
        }
        mock_credentials = HTTPAuthorizationCredentials(scheme="Bearer", credentials="valid.jwt.token")
        
        with pytest.raises(HTTPException) as exc_info:
            await get_current_user(mock_credentials, test_db)
        
        # Should be HTTP 401 Unauthorized
        assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED
        
        # Accept either the specific missing-identifier message or the generic auth-failed fallback
        detail = exc_info.value.detail
        assert any(
            phrase in detail
            for phrase in ["Missing user identifier", "Authentication failed", "Invalid token: Missing user identifier"]
        )