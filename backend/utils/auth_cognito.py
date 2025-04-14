import os
import requests
import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jwt import PyJWKClient
from sqlalchemy.orm import Session

from database import get_db
from models.db_models import User

# Cognito config from environment variables
COGNITO_REGION = os.getenv("COGNITO_REGION", "us-east-1")
COGNITO_USER_POOL_ID = os.getenv("COGNITO_USER_POOL_ID", "your-pool-id")
COGNITO_CLIENT_ID = os.getenv("COGNITO_CLIENT_ID", "your-client-id")

# JWKS URL
JWKS_URL = f"https://cognito-idp.{COGNITO_REGION}.amazonaws.com/{COGNITO_USER_POOL_ID}/.well-known/jwks.json"

security = HTTPBearer()

# Token verification function
def verify_cognito_jwt(token: str):
    try:
        jwk_client = PyJWKClient(JWKS_URL)
        signing_key = jwk_client.get_signing_key_from_jwt(token)
        payload = jwt.decode(
            token,
            signing_key.key,
            algorithms=["RS256"],
            audience=COGNITO_CLIENT_ID,
            options={"verify_exp": True},
        )
        return payload
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid or expired token: {str(e)}"
        )

# FastAPI dependency to get current user from token
async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    token = credentials.credentials
    payload = verify_cognito_jwt(token)
    
    # Get the Cognito user ID from the token
    cognito_id = payload.get('sub')
    if not cognito_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token: Missing user identifier"
        )
    
    # Try to find user in the database
    user = db.query(User).filter(User.cognito_id == cognito_id).first()
    
    # If user doesn't exist yet, create a new user record
    if not user:
        email = payload.get('email')
        if not email:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not registered in the system"
            )
            
        # Extract user details from token
        given_name = payload.get('given_name', '')
        family_name = payload.get('family_name', '')
        phone = payload.get('phone_number', '')
        
        # Create new user entry
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

# Optional role-based access control
def require_role(allowed_roles: list):
    async def role_checker(user: User = Depends(get_current_user)):
        # In a real implementation, you would check the user's roles
        # This is a placeholder for when you implement roles in your system
        
        # For now, we assume all users have basic access
        # You can replace this with actual role checking logic later
        roles = ["user"]  # Default role
        
        for role in allowed_roles:
            if role in roles:
                return True
                
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Insufficient permissions. Required roles: {allowed_roles}"
        )
    return role_checker