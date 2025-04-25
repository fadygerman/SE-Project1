import logging
import os
import jwt
from jwt import PyJWKClient

from exceptions.auth import ConfigurationError, InvalidTokenException

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
        # Log token information for debugging (header only, not the full token)
        header = jwt.get_unverified_header(token)
        logging.info(f"Verifying token with kid: {header.get('kid')}, alg: {header.get('alg')}")
        logging.info(f"Using JWKS URL: {JWKS_URL}")
        
        # Create JWKS client with proper timeout
        jwk_client = PyJWKClient(JWKS_URL, timeout=10)
        
        # Get signing key
        try:
            signing_key = jwk_client.get_signing_key_from_jwt(token)
        except jwt.exceptions.PyJWKClientError as e:
            logging.error(f"JWKS key error: {str(e)}")
            raise InvalidTokenException(f"Token verification failed: {str(e)}")
        
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
        logging.error(f"Token verification error: {str(e)}")
        raise InvalidTokenException()