from fastapi import APIRouter, HTTPException, status
from typing import List
from models.models import User

router = APIRouter(
    prefix="/users",
    tags=["users"]
)

# Sample data
users_db = [
    {
        "id": 1,
        "first_name": "John",
        "last_name": "Doe",
        "email": "john.doe@example.com",
        "phone_number": "+14155552671",
        "password_hash": "$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW"  # "password"
    },
    {
        "id": 2,
        "first_name": "Jane",
        "last_name": "Smith",
        "email": "jane.smith@example.com",
        "phone_number": "+14155552672",
        "password_hash": "$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW"
    }
]

# Get all users endpoint
@router.get("/", response_model=List[User])
async def get_users():
    return users_db

# Get user by ID endpoint
@router.get("/{user_id}", response_model=User)
async def get_user(user_id: int):
    for user in users_db:
        if user["id"] == user_id:
            return user
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"User with ID {user_id} not found"
    )