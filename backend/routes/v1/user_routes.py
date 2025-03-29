from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from passlib.hash import bcrypt

from database import get_db
from models.db_models import User as UserModel
from models.models import User, UserRegister
from utils.cognito import register_user, confirm_signup

router = APIRouter(
    prefix="/users",
    tags=["users"]
)

# Get all users endpoint
@router.get("/", response_model=List[User])
async def get_users(db: Session = Depends(get_db)):
    users = db.query(UserModel).all()
    return users

# Get user by ID endpoint
@router.get("/{user_id}", response_model=User)
async def get_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(UserModel).filter(UserModel.id == user_id).first()
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with ID {user_id} not found"
        )
    return user

@router.post("/register", status_code=status.HTTP_201_CREATED)
async def register(user_data: UserRegister, db: Session = Depends(get_db)):
    # Check if user already exists in the database
    existing_user = db.query(UserModel).filter(UserModel.email == user_data.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
        
    # Register user in Cognito
    cognito_response = register_user(
        user_data.email, 
        user_data.password,
        {
            'first_name': user_data.first_name,
            'last_name': user_data.last_name,
            'phone_number': user_data.phone_number
        }
    )
    
    if not cognito_response['success']:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=cognito_response['message']
        )
    
    # Create user in database
    cognito_user_id = cognito_response['user_id']
    hashed_password = bcrypt.hash(user_data.password)
    
    new_user = UserModel(
        first_name=user_data.first_name,
        last_name=user_data.last_name,
        email=user_data.email,
        phone_number=user_data.phone_number,
        password_hash=hashed_password,
        cognito_id=cognito_user_id  # You'll need to add this field to your User model
    )
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    return {
        "message": "User registered successfully. Please check your email for verification code.",
        "user_id": new_user.id
    }

# Confirmation endpoint
@router.post("/confirm-registration")
async def confirm_registration(email: str, confirmation_code: str):
    result = confirm_signup(email, confirmation_code)
    if not result['success']:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=result['message']
        )
    
    return {"message": "Registration confirmed successfully"}