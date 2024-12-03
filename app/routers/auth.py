# app/routers/auth.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import timedelta,datetime
import logging

from app.database import get_db
from app.models import User, UserRole
from app.schemas import LoginRequest, UserCreate, UserResponse, Token, EmailVerification
from app.security import SecurityService
from app.constants import ACCESS_TOKEN_EXPIRE_MINUTES
from app.services.email_service import email_service

router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post("/signup", response_model=UserResponse)
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    """
    User signup endpoint
    
    Args:
        user (UserCreate): User registration details
        db (Session): Database session
    
    Returns:
        UserResponse: Created user details
    
    Raises:
        HTTPException: If email already exists
    """
    # Check if user already exists
    existing_user = db.query(User).filter(User.email == user.email).first()
    if existing_user:
        raise HTTPException( #Take predfined error
            status_code=400, 
            detail="Email already registered"
        )
    
    # Hash password
    hashed_password = SecurityService.hash_password(user.password)
    
    # Generate verification token
    verification_token = SecurityService.generate_verification_token()

    
    # Create new user
    new_user = User(
        email=user.email,
        hashed_password=hashed_password,
        is_active=True,
        is_verified=False,
        role=user.role,
        verification_token=verification_token,
        verification_token_expires_at=datetime.utcnow() + timedelta(minutes=30)
    )
    
    try:
        db.add(new_user)
        
        # Send verification email
        email_service.send_verification_email(
            new_user.email, 
            verification_token
        )
        db.commit()
        db.refresh(new_user)
        return new_user
    except Exception as e:
        db.rollback()
        logging.error(f"User signup failed: {str(e)}")
        raise HTTPException(
            status_code=500, 
            detail="User registration failed"
        )

# verification should not be include in auth
@router.get("/verify-email")
def verify_email(
    token: str, 
    db: Session = Depends(get_db)
):
    """
    Email verification endpoint
    
    Args:
        verification (EmailVerification): Verification token
        db (Session): Database session
    
    Returns:
        dict: Verification status
    
    Raises:
        HTTPException: If verification fails
    """
    user = db.query(User).filter(
        User.verification_token == token ## new class for token
    ).first()
    
    if not user:
        raise HTTPException(
            status_code=400, 
            detail="Invalid verification token"
        )
    
    # Check token expiration
    if user.verification_token_expires_at < datetime.utcnow():
        raise HTTPException(
            status_code=400, 
            detail="Verification token expired"
        )
    
    # Mark user as verified
    user.is_verified = True
    user.verification_token = None
    user.verification_token_expires_at = None
    
    db.commit()
    
    return {"message": "Email verified successfully",
            "success":True}

@router.post("/login", response_model=Token)
def login(
    login_data: LoginRequest, 
    db: Session = Depends(get_db)
):
    """
    User login endpoint
    
    Args:
        login_data (LoginRequest): Login credentials
        db (Session): Database session
    
    Returns:
        Token: JWT access token
    
    Raises:
        HTTPException: If login fails
    """
    user = db.query(User).filter(User.email == login_data.email).first()
    
    if not user or not SecurityService.verify_password(login_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password"
        )
    
    if not user.is_verified:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Email not verified"
        )
    
    # Create access token
    access_token = SecurityService.create_access_token(
        data={"sub": str(user.id)},
        expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    
    return {
        "access_token": access_token, 
        "token_type": "bearer",
        "success":True
    }