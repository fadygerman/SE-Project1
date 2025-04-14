from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from database import get_db
from models.db_models import User
from models.pydantic.user import UserRegister
from utils.auth_cognito import get_current_user

router = APIRouter(
    prefix="/auth",
    tags=["auth"]
)

@router.post("/register-cognito-user", status_code=status.HTTP_201_CREATED)
async def register_cognito_user(
    user_data: UserRegister, 
    db: Session = Depends(get_db)
):
    """
    Create a user record after successful Cognito registration.
    This endpoint is called by the frontend after a successful Cognito signup.
    """
    # Check if user already exists
    existing_user = db.query(User).filter(User.cognito_id == user_data.cognito_id).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User already exists"
        )
    
    # Create new user
    db_user = User(
        first_name=user_data.first_name,
        last_name=user_data.last_name,
        email=user_data.email,
        phone_number=user_data.phone_number,
        cognito_id=user_data.cognito_id,
        # No need to store password_hash since Cognito handles authentication
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