from sqlalchemy import Column, Integer, String, DateTime, Boolean, Enum
from sqlalchemy.sql import func
from app.database import Base
import enum

class UserRole(enum.Enum):
    OPS_USER = 'ops_user'
    CLIENT_USER = 'client_user'

class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    role = Column(Enum(UserRole), nullable=False)
    verification_token = Column(String(255))
    verification_token_expires_at = Column(DateTime)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class File(Base):
    __tablename__ = 'files'

    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String(255), nullable=False)
    s3_key = Column(String(255), nullable=False)
    uploaded_by = Column(Integer, nullable=False)
    file_type = Column(String(10), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())