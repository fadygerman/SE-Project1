from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
import os

from database import get_db
from models.db_models import User
from models.pydantic.user import UserRegister
from services.auth_service import get_current_user
from services.cognito_service import verify_cognito_jwt
from exceptions.auth import UnauthorizedException, ForbiddenException

router = APIRouter(
    prefix="/auth",
    tags=["auth"]
)

security = HTTPBearer()

@router.post("/register-cognito-user", status_code=status.HTTP_201_CREATED)
async def register_cognito_user(
    user_data: UserRegister, 
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    """
    Create a user record after successful Cognito registration.
    This endpoint is called by the frontend after a successful Cognito signup.
    """
    # Verify the token first
    try:
        token = credentials.credentials
        payload = verify_cognito_jwt(token)
        token_cognito_id = payload.get("sub")
        
        # Verify token cognito_id matches the one in registration data
        if token_cognito_id != user_data.cognito_id:
            raise ForbiddenException(
                detail="Cognito ID in token does not match provided ID"
            )
            
    except UnauthorizedException as e:
        # Pass through our custom exceptions
        raise 
    except Exception as e:
        raise UnauthorizedException(
            detail=f"Invalid token: {str(e)}"
        )
    
    # Check if user already exists
    existing_user = db.query(User).filter(User.cognito_id == user_data.cognito_id).first()
    if existing_user:
        # Update existing user instead of error
        existing_user.first_name = user_data.first_name
        existing_user.last_name = user_data.last_name
        existing_user.phone_number = user_data.phone_number
        db.commit()
        db.refresh(existing_user)
        return {"id": existing_user.id, "message": "User profile updated successfully"}
    
    # Create new user
    db_user = User(
        first_name=user_data.first_name,
        last_name=user_data.last_name,
        email=user_data.email,
        phone_number=user_data.phone_number,
        cognito_id=user_data.cognito_id,
    )
    
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return {"id": db_user.id, "message": "User registered successfully"}

# Public endpoint that doesn't require authentication - for testing
@router.get("/public")
async def public_endpoint():
    """Public endpoint that doesn't require authentication"""
    return {"message": "This is a public endpoint"}

# Protected endpoint - for testing authentication
@router.get("/protected")
async def protected_endpoint(current_user: User = Depends(get_current_user)):
    """Protected endpoint that requires authentication"""
    return {
        "message": "Authentication successful", 
        "user_id": current_user.id, 
        "email": current_user.email
    }

# For development environment only
if os.getenv("DEVELOPMENT_MODE", "False").lower() == "true":
    @router.get("/debug/token-info")
    async def debug_token_info(
        credentials: HTTPAuthorizationCredentials = Depends(security)
    ):
        """Debug endpoint to check token information"""
        token = credentials.credentials
        payload = verify_cognito_jwt(token)
        return {"token_info": payload}