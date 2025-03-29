import os
from fastapi import APIRouter, Request, Depends
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session

from database import get_db
from models.db_models import User as UserModel
from utils.auth import oauth, get_current_user

router = APIRouter(
    prefix="/auth",
    tags=["auth"]
)

# web-based login endpoint
@router.get("/login")
async def login(request: Request):
    # Get the redirect URI - this needs to be configured in Cognito
    redirect_uri = request.url_for('authorize')
    return await oauth.cognito.authorize_redirect(request, redirect_uri)

# callback handler
@router.get("/authorize")
async def authorize(request: Request, db: Session = Depends(get_db)):
    # Complete the oauth flow
    token = await oauth.cognito.authorize_access_token(request)
    user_info = token.get('userinfo')
    
    # Store user info in session
    request.session['user'] = user_info
    
    # Get or create user in database
    email = user_info.get('email')
    user = db.query(UserModel).filter(UserModel.email == email).first()
    
    if not user:
        # User exists in Cognito but not in our DB - create them
        user = UserModel(
            first_name=user_info.get('given_name', ''),
            last_name=user_info.get('family_name', ''),
            email=email,
            phone_number=user_info.get('phone_number', ''),
            cognito_id=user_info.get('sub')
        )
        db.add(user)
        db.commit()
    
    # Redirect to frontend application
    return RedirectResponse(url="/")

@router.get("/logout")
async def logout(request: Request):
    # Clear session
    request.session.pop('user', None)
    
    # Redirect to Cognito logout URL
    cognito_logout_url = f"https://{os.environ.get('COGNITO_DOMAIN')}.auth.{os.environ.get('AWS_REGION')}.amazoncognito.com/logout"
    return RedirectResponse(url=cognito_logout_url)

# check authentication
@router.get("/me")
async def read_users_me(current_user: dict = Depends(get_current_user)):
    return current_user