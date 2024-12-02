# app/routers/file_operations.py
from fastapi import APIRouter, File, UploadFile, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List,Dict,Any
import os

from app.constants import ALLOWED_FILE_EXTENSIONS
from app.database import get_db
from app.models import User, File as FileModel, UserRole
from app.schemas import FileResponse,DownloadResponse
from app.security import SecurityService
from app.services.s3_service import s3_service

router = APIRouter(prefix="/files", tags=["File Operations"])


def convert_sqlalchemy_to_dict(model_instance: FileModel) -> Dict[str, Any]:
    """
    Convert a SQLAlchemy model instance to a dictionary
    """
    return {
        "id": model_instance.id,
        "filename": model_instance.filename,
        "s3_key": model_instance.s3_key,
        "uploaded_by": model_instance.uploaded_by,
        "file_type": model_instance.file_type,
        "created_at": model_instance.created_at
    }

def validate_file_type(filename: str):
    """
    Validate file type based on allowed extensions

    Args:
        filename (str): Name of the file to validate

    Raises:
        HTTPException: If file type is not allowed
    """
    file_ext = os.path.splitext(filename)[1].lower()
    if file_ext not in ALLOWED_FILE_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"File type {file_ext} not allowed. Allowed types: {', '.join(ALLOWED_FILE_EXTENSIONS)}",
        )


@router.post("/upload", response_model=FileResponse)
def upload_file(
    file: UploadFile ,
    current_user: User = Depends(SecurityService.get_current_user),
    db: Session = Depends(get_db),
):
    """
    File upload endpoint (Ops User only)

    Args:
        file (UploadFile): File to upload
        current_user (User): Authenticated user
        db (Session): Database session

    Returns:
        FileResponse: Uploaded file metadata

    Raises:
        HTTPException: If user is not an Ops User or file validation fails
    """
    # print(file.filename)
    # Validate user role
    if current_user.role != UserRole.OPS_USER:
        raise HTTPException(status_code=403, detail="Only Ops Users can upload files")

    # Validate file type
    validate_file_type(file.filename)

    try:
        # Upload to S3
        print(file.file)
        s3_key = s3_service.upload_file(file.file, file.filename, file.content_type)

        # Save file metadata to database
        db_file = FileModel(
            filename=file.filename,
            s3_key=s3_key,
            uploaded_by=current_user.id,
            file_type=os.path.splitext(file.filename)[1].lower(),
        )

        db.add(db_file)
        db.commit()
        db.refresh(db_file)

        return convert_sqlalchemy_to_dict(db_file)


    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/list")
def list_files(
    current_user: User = Depends(SecurityService.get_current_user),
    db: Session = Depends(get_db),
):
    """
    List all uploaded files

    Args:
        current_user (User): Authenticated user
        db (Session): Database session

    Returns:
        List[FileResponse]: List of uploaded files
    """
    # Only allow client users to list files
    if current_user.role != UserRole.CLIENT_USER: 
        raise HTTPException(status_code=403, detail="Only Client Users can list files")

    files = db.query(FileModel).all()
    return files



@router.get("/download/{file_id}", response_model=DownloadResponse)
def download_file(
    file_id: int,
    current_user: User = Depends(SecurityService.get_current_user),
    db: Session = Depends(get_db),
):
    """
    Generate a secure download link for a file

    Args:
        file_id (int): ID of the file to download
        current_user (User): Authenticated user
        db (Session): Database session

    Returns:
        DownloadResponse: Secure download link and success message

    Raises:
        HTTPException: If file not found or user not authorized
    """
    try:
        # Only allow client users to download files
        if current_user.role != UserRole.CLIENT_USER:
            raise HTTPException(
                status_code=403, detail="Only Client Users can download files"
            )

        # Find the file
        file = db.query(FileModel).filter(FileModel.id == file_id).first()
        if not file:
            raise HTTPException(status_code=404, detail="File not found")

        # Generate pre-signed URL
        download_link = s3_service.generate_presigned_url(file.s3_key)

        return {
            "download_link": download_link, 
            "success": True
        }

    except Exception as e:
        # Log the actual exception
        print(f"Download file error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")
