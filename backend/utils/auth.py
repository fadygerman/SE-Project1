from fastapi import FastAPI, Request, Response, Depends, HTTPException, status
from fastapi.responses import RedirectResponse
from authlib.integrations.starlette_client import OAuth
from starlette.middleware.sessions import SessionMiddleware
import os

# OAuth client setup
oauth = OAuth()
oauth.register(
    name='cognito',
    client_id=os.environ.get('COGNITO_CLIENT_ID'),
    client_secret=os.environ.get('COGNITO_SECRET'),
    server_metadata_url=f"https://cognito-idp.{os.environ.get('AWS_REGION')}.amazonaws.com/{os.environ.get('COGNITO_USER_POOL_ID')}/.well-known/openid-configuration",
    client_kwargs={'scope': 'openid email profile phone'},
)

# Function to configure auth in the main app
def configure_auth(app: FastAPI):
    # Add session middleware for auth state
    app.add_middleware(
        SessionMiddleware, 
        secret_key=os.environ.get('TOKEN_SIGNATURE_KEY')
    )

# Dependency to get user from session
async def get_current_user(request: Request):
    user = request.session.get('user')
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated"
        )
    return user