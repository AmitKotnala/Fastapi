import secrets
from datetime import datetime, timedelta
from typing import Optional, Union

from app.constants import ALGORITHM, SECRET_KEY
from jose import jwt,JWTError
import bcrypt
from fastapi import Depends, HTTPException, Security
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.models import User, UserRole
from app.database import get_db

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")



class SecurityService:
    @staticmethod
    def hash_password(password: str) -> str:
        """
        Hash a password using bcrypt

        Args:
            password (str): Plain text password

        Returns:
            str: Hashed password
        """
        return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")

    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """
        Verify a password against its hash

        Args:
            plain_password (str): Plain text password
            hashed_password (str): Hashed password to compare against

        Returns:
            bool: True if password matches, False otherwise
        """
        return bcrypt.checkpw(
            plain_password.encode("utf-8"), hashed_password.encode("utf-8")
        )

    @staticmethod
    def create_access_token(
        data: dict, expires_delta: Optional[timedelta] = None
    ) -> str:
        """
        Create a JWT access token

        Args:
            data (dict): Payload data for token
            expires_delta (Optional[timedelta]): Token expiration time

        Returns:
            str: JWT access token
        """
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=15)

        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(
            to_encode, SECRET_KEY, algorithm=ALGORITHM
        )
        return encoded_jwt

    @staticmethod
    def generate_verification_token() -> str:
        """
        Generate a secure email verification token

        Returns:
            str: Secure verification token
        """
        return secrets.token_urlsafe(32)

    @staticmethod
    def decode_token(token: str) -> dict:
        """
        Decode a JWT token

        Args:
            token (str): JWT token to decode

        Returns:
            dict: Decoded token payload

        Raises:
            HTTPException: If token is invalid or expired
        """
        try:
            print(SECRET_KEY,'\n',token)
            return jwt.decode(
                token=token, key =SECRET_KEY, algorithms=[ALGORITHM]
            )
        except Exception as JWTError:
            raise HTTPException(status_code=401, detail=f"{JWTError}")
        # except jwt.InvalidTokenError:
        #     raise HTTPException(status_code=401, detail="Invalid token")

    @staticmethod
    def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> Union[User, None]:

        """
        Get current user from JWT token

        Args:
            token (str): JWT access token
            db (Session): Database session

        Returns:
            User: Authenticated user

        Raises:
            HTTPException: If user not found or token is invalid
        """
        try:
            print('STarting....',token)
            payload = SecurityService.decode_token(token)
            print('running...')
            user_id: int = payload.get("sub")
            print('running...')
            if user_id is None:
                raise HTTPException(
                    status_code=401, detail="Could not validate credentials"
                )

            user = db.query(User).filter(User.id == user_id).first()
            print('running...')
            if not user:
                raise HTTPException(status_code=401, detail="User not found")

            return user
        except Exception as e:
            raise HTTPException(status_code=401, detail=str(e))
