import hmac
import hashlib
import base64
import os
import logging
import boto3
from botocore.exceptions import ClientError
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Get Cognito configuration from environment variables
# Global config
USER_POOL_ID = os.environ.get('COGNITO_USER_POOL_ID')
CLIENT_ID = os.environ.get('COGNITO_CLIENT_ID')
CLIENT_SECRET = os.environ.get('COGNITO_SECRET')
REGION = os.environ.get('AWS_REGION', 'eu-north-1')
DEVELOPMENT_MODE = os.environ.get('DEVELOPMENT_MODE', 'False').lower() == 'true'

# Create Cognito client
client = boto3.client('cognito-idp', region_name=REGION)

def register_user(email, password, attributes):
    """Register a new user in Cognito User Pool"""
    logger.info(f"Attempting to register {email} in Cognito...")
    logger.info(f"Using USER_POOL_ID: {USER_POOL_ID}, CLIENT_ID: {CLIENT_ID}, REGION: {REGION}")
    
    # Development mode - mock successful registration
    if DEVELOPMENT_MODE:
        logger.info("Development mode: Mocking user registration.")
        return {
            'success': True,
            'user_id': f"dev-{email}",
            'message': 'Development mode: User registered successfully.'
        }
    
    try:
        # Generate the secret hash
        secret_hash = get_secret_hash(email)
        
        # Register user in Cognito
        response = client.sign_up(
            ClientId=CLIENT_ID,
            SecretHash=secret_hash,
            Username=email,
            Password=password,
            UserAttributes=[
                {
                    'Name': 'email',
                    'Value': email
                },
                {
                    'Name': 'given_name',  # Changed from 'name'
                    'Value': attributes['first_name']
                },
                {
                    'Name': 'family_name',  # Added as separate attribute
                    'Value': attributes['last_name']
                },
                {
                    'Name': 'phone_number',
                    'Value': attributes['phone_number']
                }
            ]
        )
        logger.info(f"Successfully registered in Cognito with ID: {response['UserSub']}")
        return {
            'success': True,
            'user_id': response['UserSub'],
            'message': 'User registered successfully. Please check your email for verification.'
        }
    except ClientError as e:
        error_code = e.response['Error']['Code']
        error_message = e.response['Error']['Message']
        logger.error(f"Cognito error: {error_code} - {error_message}")
        return {
            'success': False,
            'error': error_code,
            'message': error_message
        }

def confirm_signup(username, confirmation_code):
    """Confirm user registration with verification code"""
    logger.info(f"Attempting to confirm signup for user: {username}")
    
    # Development mode
    if DEVELOPMENT_MODE:
        logger.info("Development mode: Mocking confirmation.")
        return {
            'success': True,
            'message': 'Development mode: User confirmed successfully'
        }
    
    try:
        # Generate the secret hash
        secret_hash = get_secret_hash(username)
        
        # Confirm signup in Cognito
        client.confirm_sign_up(
            ClientId=CLIENT_ID,
            SecretHash=secret_hash,
            Username=username,
            ConfirmationCode=confirmation_code
        )
        logger.info(f"Successfully confirmed signup for user: {username}")
        return {
            'success': True,
            'message': 'User confirmed successfully'
        }
    except ClientError as e:
        error_code = e.response['Error']['Code']
        error_message = e.response['Error']['Message']
        logger.error(f"Cognito error: {error_code} - {error_message}")
        return {
            'success': False,
            'error': error_code,
            'message': error_message
        }
    
def get_secret_hash(username):
    """Calculate the SECRET_HASH required for Cognito API calls"""
    message = username + CLIENT_ID
    dig = hmac.new(
        key=CLIENT_SECRET.encode('utf-8'),
        msg=message.encode('utf-8'),
        digestmod=hashlib.sha256
    ).digest()
    return base64.b64encode(dig).decode()

CLIENT_SECRET = os.environ.get('COGNITO_SECRET')