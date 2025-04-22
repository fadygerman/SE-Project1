import logging
import os
import jwt
from jwt import PyJWKClient
import sys

from exceptions.auth import ConfigurationError, InvalidTokenException

logger = logging.getLogger(__name__)

# Cognito configuration
COGNITO_REGION = os.getenv("COGNITO_REGION", "eu-north-1")
COGNITO_USER_POOL_ID = os.getenv("COGNITO_USER_POOL_ID")
COGNITO_CLIENT_ID = os.getenv("COGNITO_CLIENT_ID")

if not COGNITO_USER_POOL_ID:
    raise ConfigurationError("Missing required environment variable: COGNITO_USER_POOL_ID")

if not COGNITO_CLIENT_ID:
    raise ConfigurationError("Missing required environment variable: COGNITO_CLIENT_ID")


# JWKS URL
JWKS_URL = f"https://cognito-idp.{COGNITO_REGION}.amazonaws.com/{COGNITO_USER_POOL_ID}/.well-known/jwks.json"

def verify_cognito_jwt(token: str):
    """Verify a JWT token from AWS Cognito"""
    try:
        # Create JWKS client with proper timeout
        print(">>> JWKS_URL is:", JWKS_URL, file=sys.stderr)
        jwk_client = PyJWKClient(JWKS_URL)

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
        logger.exception("JWT verification failed")
        raise InvalidTokenException()