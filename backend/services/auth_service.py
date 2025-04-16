from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from database import get_db
from models.db_models import User, UserRole
from exceptions.auth import (
    MissingUserIdentifierException, 
    UserNotRegisteredException,
    IncompleteUserDataException
)
from services.cognito_service import verify_cognito_jwt

# Security scheme for JWT Bearer tokens
security = HTTPBearer()

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
            given_name = payload.get('given_name', '')
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
    except MissingUserIdentifierException as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=e.message
        )
    except UserNotRegisteredException as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=e.message
        )
    except IncompleteUserDataException as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=e.message
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication failed"
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
        
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Access denied. Required role: {', '.join(allowed_roles)}"
        )
    return role_checker

async def get_booking_with_permission_check(
    booking_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Check if the user has permission to access the specified booking"""
    from models.db_models import Booking as BookingDB
    
    booking = db.query(BookingDB).filter(BookingDB.id == booking_id).first()
    
    if booking is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Booking with ID {booking_id} not found"
        )
    
    # Check if it's the user's booking or if they have admin role
    if booking.user_id != current_user.id and current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, 
            detail="You can only access your own bookings"
        )
    
    return booking