'''
Pydantic models, provided by the Pydantic library 
(a data validation and settings management library in Python), 
are used to validate incoming data, serialize outgoing data, 
and define the structure of the data used in the application.
'''
from enum import Enum
from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator

from models.db_models import UserRole


class User(BaseModel):
    id: int
    first_name: str = Field(description="User's first name", min_length=1, max_length=50)
    last_name: str = Field(description="User's last name", min_length=1, max_length=50) 
    email: EmailStr = Field(description="User's email address")
    phone_number: str = Field(description="User's phone number")
    cognito_id: str = Field(description="AWS Cognito user ID")
    role: UserRole = Field(default=UserRole.USER, description="User's role")
    
    model_config = ConfigDict(from_attributes=True)    
    @field_validator('phone_number')
    @classmethod
    def validate_phone(cls, v):
        # Basic phone validation - can be enhanced based on your specific requirements
        if not v or len(v) < 8:
            raise ValueError('Phone number must be at least 8 characters')
        return v

    
class UserRegister(BaseModel):
    first_name: str = Field(description="User's first name", min_length=1, max_length=50)
    last_name: str = Field(description="User's last name", min_length=1, max_length=50)
    email: EmailStr = Field(description="User's email address")
    phone_number: str = Field(description="User's phone number")
    cognito_id: str = Field(description="AWS Cognito user ID (sub claim)")
    
    @field_validator('phone_number')
    @classmethod
    def validate_phone(cls, v):
        if not v or len(v) < 8:
            raise ValueError('Phone number must be at least 8 characters')
        return v