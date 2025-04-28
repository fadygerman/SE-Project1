from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from database import get_db
from models.db_models import User as UserModel, UserRole
from models.pydantic.user import User
from services.auth_service import get_current_user, require_role

router = APIRouter(
    prefix="/users",
    tags=["users"]
)

# Get all users endpoint - restricted to admin role
@router.get("/", response_model=list[User])
async def get_users(
    db: Session = Depends(get_db),
    _=Depends(require_role([UserRole.ADMIN]))  # Only admins can list all users
):
    users = db.query(UserModel).all()
    return users

# Get user by ID endpoint - users can only access their own data
@router.get("/{user_id}", response_model=User)
async def get_user(
    user_id: int, 
    db: Session = Depends(get_db), 
    current_user: UserModel = Depends(get_current_user)
):
    # If user is trying to access someone else's data and is not an admin,
    # return 403 Forbidden
    if user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only access your own user data"
        )
    
    user = db.query(UserModel).filter(UserModel.id == user_id).first()
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with ID {user_id} not found"
        )
    return user

# Get current user profile
@router.get("/me/profile", response_model=User)
async def get_my_profile(current_user: UserModel = Depends(get_current_user)):
    """Get the profile of the currently authenticated user"""
    return current_user