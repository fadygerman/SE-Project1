import logging

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jwt import PyJWTError
from sqlalchemy.orm import Session

from database import get_db
from exceptions.auth import IncompleteUserDataException, InvalidTokenException, MissingUserIdentifierException, UserNotRegisteredException
from models.db_models import User
from services.cognito_service import verify_cognito_jwt

# Security scheme for JWT Bearer tokens
security = HTTPBearer()

logger = logging.getLogger(__name__)

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    """
    Get the current authenticated user based on the JWT token.
    If the user doesn't exist in the database but is authenticated with Cognito,
    create a new user record.
    """
    try:
        token = credentials.credentials
        payload = verify_cognito_jwt(token)
        
        # Get user info from payload
        cognito_id = payload.get("sub")
        if not cognito_id:
            raise MissingUserIdentifierException()
        
        # Find user by Cognito ID
        user = db.query(User).filter(User.cognito_id == cognito_id).first()
        if not user:
            # Extract email from payload
            email = payload.get("email")
            if not email:
                raise UserNotRegisteredException()
            
            # Extract user details from token
            given_name = payload.get('name', '')
            if not given_name and payload.get('given_name'):
                given_name = payload.get('given_name')
            family_name = payload.get('family_name', '')
            phone = payload.get('phone_number', '')
            
            # Check if all required data is present
            if not given_name or len(given_name) < 1:
                raise IncompleteUserDataException("first_name")
                
            if not family_name or len(family_name) < 1:
                raise IncompleteUserDataException("last_name")
                
            if not phone or len(phone) < 8:
                raise IncompleteUserDataException("phone_number")
            
            # Create new user entry with validated data
            user = User(
                email=email,
                first_name=given_name,
                last_name=family_name,
                phone_number=phone,
                cognito_id=cognito_id
            )
            db.add(user)
            db.commit()
            db.refresh(user)
            
        return user
    except HTTPException:
        raise
    except (PyJWTError, InvalidTokenException) as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token" # Consistent detail for all token errors
        )
    except (
        MissingUserIdentifierException, 
        UserNotRegisteredException,
        IncompleteUserDataException
        ) as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=e.message
        )
    except Exception as e:
        logger.error("Unexpected error during user authentication/creation: %s", e, exc_info=True)
        # Raise a 500 Internal Server Error for unexpected issues
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An internal error occurred during authentication."
        )

# Role-based access control
def require_role(allowed_roles):
    """Check if user has one of the required roles"""
    async def role_checker(user: User = Depends(get_current_user)):
        # If no roles provided, any authenticated user is allowed
        if not allowed_roles:
            return True
        
        # Check if user has one of the allowed roles
        if user.role in allowed_roles:
            return True
        
        # Convert each enum to its string value for a clearer error message
        role_names = [r.value for r in allowed_roles]
        
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Access denied. Required role: {', '.join(role_names)}"
        )
    return role_checker
