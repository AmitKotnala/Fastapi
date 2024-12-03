import boto3
import os
import base64
import json
from typing import BinaryIO, Dict, Optional
from datetime import datetime, timedelta
from botocore.exceptions import ClientError
from fastapi import HTTPException
from cryptography.fernet import Fernet

from app.constants import AWS_CLIENT_ID, AWS_BUCKET_NAME, AWS_CLIENT_KEY, AWS_REGION
from app.services.logging_config import Logger

class S3Service:
    """
    Service for handling file uploads, downloads, and secure token generation with AWS S3
    """
    def __init__(self):
        """
        Initialize S3 client with AWS credentials and encryption
        """
        self.s3_client = boto3.client(
            service_name='s3',
            aws_access_key_id=AWS_CLIENT_ID,
            aws_secret_access_key=AWS_CLIENT_KEY,
            region_name=AWS_REGION
        )
        self.bucket_name = AWS_BUCKET_NAME
        
        # Initialize encryption for secure download tokens
        self.encryption_key = Fernet.generate_key()
        self.fernet = Fernet(self.encryption_key)

    def upload_file(
        self, 
        file: BinaryIO, 
        filename: str, 
        content_type: str
    ) -> str:
        """
        Upload file to S3 bucket
        
        Args:
            file (BinaryIO): File object to upload
            filename (str): Name of the file
            content_type (str): MIME type of the file
        
        Returns:
            str: S3 key of the uploaded file
        
        Raises:
            HTTPException: If file upload fails
        """
        try:
            # Generate a unique key for the file
            s3_key = f"fast_api/uploads/{filename}"
            
            self.s3_client.upload_fileobj(
                file, 
                self.bucket_name, 
                s3_key,
                ExtraArgs={
                    'ContentType': content_type
                }
            )
            return s3_key
        except ClientError as e:
            raise HTTPException(
                status_code=500, 
                detail=f"S3 upload failed: {str(e)}"
            )

    def generate_presigned_url(
        self, 
        s3_key: str, 
        expiration: int = 900
    ) -> str:
        """
        Generate a pre-signed URL for secure file download
        
        Args:
            s3_key (str): S3 key of the file
            expiration (int, optional): URL expiration time in seconds. Defaults to 15 minutes.
        
        Returns:
            str: Pre-signed URL for file download
        
        Raises:
            HTTPException: If URL generation fails
        """
        try:
            url = self.s3_client.generate_presigned_url(
                'get_object',
                Params={
                    'Bucket': self.bucket_name,
                    'Key': s3_key
                },
                ExpiresIn=expiration
            )
            return url
        except ClientError as e:
            raise HTTPException(
                status_code=500, 
                detail=f"Failed to generate download URL: {str(e)}"
            )

    def download_file(self, s3_key: str) -> bytes:
        """
        Download file contents from S3
        
        Args:
            s3_key (str): S3 key of the file to download
        
        Returns:
            bytes: File contents
        
        Raises:
            HTTPException: If file download fails
        """
        try:
            response = self.s3_client.get_object(
                Bucket=self.bucket_name, 
                Key=s3_key
            )
            return response['Body'].read()
        except ClientError as e:
            raise HTTPException(
                status_code=404, 
                detail=f"File not found: {str(e)}"
            )

    def generate_download_token(
        self, 
        file_id: int, 
        user_id: int, 
        expires_in: int = 300
    ) -> str:
        """
        Generate a secure, encrypted download token
        
        Args:
            file_id (int): ID of the file to download
            user_id (int): ID of the user requesting download
            expires_in (int): Token expiration time in seconds
        
        Returns:
            str: Encrypted download token
        """
        # Create a payload with file details and expiration
        payload = {
            'file_id': file_id,
            'user_id': user_id,
            'expires_at': (datetime.utcnow() + timedelta(seconds=expires_in)).isoformat()
        }
        
        # Convert payload to JSON and encrypt
        token_data = json.dumps(payload).encode('utf-8')
        encrypted_token = self.fernet.encrypt(token_data)
        print(encrypted_token)
        # Base64 encode for safe URL transmission
        return base64.urlsafe_b64encode(encrypted_token).decode('utf-8')

    def validate_download_token(self, token: str) -> Dict:
        """
        Validate and decrypt the download token
        
        Args:
            token (str): Encrypted download token
        
        Returns:
            Dict: Decrypted token payload
        
        Raises:
            HTTPException: If token is invalid or expired
        """
        try:
            # print(token)
            # Base64 decode
            encrypted_token = base64.urlsafe_b64decode(token.encode('utf-8'))
            
            # Decrypt token
            decrypted_data = self.fernet.decrypt(encrypted_token)
            Logger.info(decrypted_data)
            payload = json.loads(decrypted_data.decode('utf-8'))
            Logger.info(payload)
            # Check expiration
            expires_at = datetime.fromisoformat(payload['expires_at'])
            Logger.info(expires_at)
            if datetime.utcnow() > expires_at:
                raise HTTPException(status_code=401, detail="Download token expired")
            
            return payload
        except Exception as e:
            raise HTTPException(status_code=401, detail="Invalid download token")

# Create a singleton instance
s3_service = S3Service()