import os
import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jwt import PyJWKClient
from sqlalchemy.orm import Session

from database import get_db
from models.db_models import User

# Cognito configuration
COGNITO_REGION = os.getenv("COGNITO_REGION", "eu-north-1")
COGNITO_USER_POOL_ID = os.getenv("COGNITO_USER_POOL_ID", "eu-north-1_3cYMEI8RB")
COGNITO_CLIENT_ID = os.getenv("COGNITO_CLIENT_ID", "2mjf5mmb10to1g4pqrgurnumql")

# JWKS URL
JWKS_URL = f"https://cognito-idp.{COGNITO_REGION}.amazonaws.com/{COGNITO_USER_POOL_ID}/.well-known/jwks.json"

security = HTTPBearer()

def verify_cognito_jwt(token: str):
    """Verify a JWT token from AWS Cognito"""
    try:
        # Create JWKS client with proper timeout
        jwk_client = PyJWKClient(JWKS_URL, timeout=10)
        
        # Get signing key
        signing_key = jwk_client.get_signing_key_from_jwt(token)
        
        # Decode and verify token
        payload = jwt.decode(
            token,
            signing_key.key,
            algorithms=["RS256"],
            options={
                "verify_exp": True,
                "verify_aud": False,  # Don't verify audience for access tokens
                "verify_iss": True,   # But do verify issuer
            },
            # Issuer should match your Cognito user pool
            issuer=f"https://cognito-idp.{COGNITO_REGION}.amazonaws.com/{COGNITO_USER_POOL_ID}"
        )
        return payload
    except Exception as e:
        # Detailed error for debugging
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid or expired token: {str(e)}"
        )

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    try:
        token = credentials.credentials
        payload = verify_cognito_jwt(token)
        
        # Get user info from payload
        cognito_id = payload.get("sub")
        if not cognito_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token: Missing user identifier"
            )
        
        # Find user by Cognito ID
        user = db.query(User).filter(User.cognito_id == cognito_id).first()
        if not user:
            # Extract email from payload
            email = payload.get("email")
            if not email:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="User not registered in the system"
                )
            
            # Extract user details from token
            given_name = payload.get('given_name', '')
            family_name = payload.get('family_name', '')
            phone = payload.get('phone_number', '')
            
            # Check if all required data is present
            if not given_name or len(given_name) < 1:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="User authenticated with Cognito but first_name is missing. Please complete registration."
                )
                
            if not family_name or len(family_name) < 1:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="User authenticated with Cognito but last_name is missing. Please complete registration."
                )
                
            if not phone or len(phone) < 8:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="User authenticated with Cognito but valid phone_number is missing. Please complete registration."
                )
            
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
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Authentication failed: {str(e)}"
        )

# Role-based access control (placeholder implementation)
def require_role(allowed_roles):
    """Check if user has one of the required roles"""
    async def role_checker(user: User = Depends(get_current_user)):
        return True  # For now, allow all authenticated users
    return role_checker