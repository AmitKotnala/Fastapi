from pydantic import BaseModel, EmailStr, ConfigDict, constr, validator
from datetime import datetime
from typing import Optional, List
from app.models import UserRole


class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class DownloadResponse(BaseModel):
    download_link: str
    message: str

class UserBase(BaseModel):
    """
    Base model for user creation and representation
    """
    email: EmailStr

class UserCreate(UserBase):
    """
    Model for user registration
    """
    password: constr(min_length=8)
    role: UserRole

    @validator('password')
    def password_complexity(cls, v):
        """
        Validate password complexity
        
        Args:
            v (str): Password to validate
        
        Raises:
            ValueError: If password doesn't meet complexity requirements
        """
        if not any(char.isdigit() for char in v):
            raise ValueError('Password must contain at least one digit')
        if not any(char.isupper() for char in v):
            raise ValueError('Password must contain at least one uppercase letter')
        return v

class UserResponse(UserBase):
    """
    Model for user response, excluding sensitive information
    """
    id: int
    is_active: bool
    is_verified: bool
    role: UserRole

    class Config:
        orm_mode = True

class Token(BaseModel):
    """
    JWT Token model
    """
    access_token: str
    token_type: str

class FileUpload(BaseModel):
    """
    Model for file upload metadata
    """
    filename: str
    file_type: str

class FileResponse(FileUpload):
    """
    Model for file response with additional metadata
    """
    id: int
    s3_key: str
    uploaded_by: int
    created_at: Optional[datetime] = None

    class Config:
        orm_mode = True

class EmailVerification(BaseModel):
    """
    Model for email verification request
    """
    token: str
