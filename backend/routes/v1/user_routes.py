from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from database import get_db
from models.db_models import User as UserModel
from models.models import User

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