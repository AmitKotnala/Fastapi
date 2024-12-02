import boto3
import os
from typing import BinaryIO
from botocore.exceptions import ClientError
from fastapi import HTTPException

from app.constants import AWS_CLIENT_ID, AWS_BUCKET_NAME, AWS_CLIENT_KEY,AWS_REGION



class S3Service:
    """
    Service for handling file uploads and downloads with AWS S3
    """
    def __init__(self):
        """
        Initialize S3 client with AWS credentials
        """
        self.s3_client = boto3.client(
            service_name = 's3',
            aws_access_key_id=AWS_CLIENT_ID,
            aws_secret_access_key=AWS_CLIENT_KEY,
            region_name = AWS_REGION
        )
        self.bucket_name = AWS_BUCKET_NAME

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

# Create a singleton instance
s3_service = S3Service()