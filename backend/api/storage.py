# backend/api/storage.py
"""
Storage API endpoints
=====================

Handles file storage operations with Azure Blob Storage.
"""

import os
import logging
from typing import List
from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import StreamingResponse

from services.storage import StorageService
from models.storage_models import (
    FileUploadResponse,
    FileListResponse,
    FileMetadata
)

logger = logging.getLogger(__name__)
router = APIRouter()

# Initialize service
storage_service = StorageService()


@router.post("/upload", response_model=FileUploadResponse)
async def upload_file(
    file: UploadFile = File(...),
    folder: str = "uploads"
):
    """
    Upload a file to Azure Blob Storage.
    
    Args:
        file: File to upload
        folder: Folder path in storage
    
    Returns:
        File metadata and storage URL
    """
    try:
        # Validate file size
        max_size_mb = int(os.getenv("MAX_UPLOAD_SIZE_MB", "50"))
        file_size = 0
        
        # Read file in chunks to check size
        chunks = []
        while chunk := await file.read(1024 * 1024):  # 1MB chunks
            chunks.append(chunk)
            file_size += len(chunk)
            if file_size > max_size_mb * 1024 * 1024:
                raise HTTPException(
                    status_code=413,
                    detail=f"File too large. Maximum size is {max_size_mb}MB"
                )
        
        # Reconstruct file content
        content = b''.join(chunks)
        
        # Upload to storage
        result = await storage_service.upload_file(
            file_name=file.filename,
            file_content=content,
            folder=folder,
            content_type=file.content_type
        )
        
        return FileUploadResponse(**result)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Upload error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/files", response_model=FileListResponse)
async def list_files(
    folder: str = "",
    prefix: str = "",
    limit: int = 100
):
    """
    List files in storage.
    
    Args:
        folder: Folder path to list
        prefix: File name prefix filter
        limit: Maximum number of files to return
    
    Returns:
        List of file metadata
    """
    try:
        files = await storage_service.list_files(
            folder=folder,
            prefix=prefix,
            limit=limit
        )
        
        return FileListResponse(
            files=[FileMetadata(**f) for f in files],
            total=len(files)
        )
        
    except Exception as e:
        logger.error(f"List files error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/download/{file_path:path}")
async def download_file(file_path: str):
    """
    Download a file from storage.
    
    Args:
        file_path: Path to file in storage
    
    Returns:
        File stream
    """
    try:
        file_stream, content_type, file_name = await storage_service.download_file(file_path)
        
        return StreamingResponse(
            file_stream,
            media_type=content_type,
            headers={
                "Content-Disposition": f"attachment; filename={file_name}"
            }
        )
        
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="File not found")
    except Exception as e:
        logger.error(f"Download error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/delete/{file_path:path}")
async def delete_file(file_path: str):
    """
    Delete a file from storage.
    
    Args:
        file_path: Path to file in storage
    
    Returns:
        Deletion confirmation
    """
    try:
        await storage_service.delete_file(file_path)
        
        return {
            "message": "File deleted successfully",
            "file_path": file_path
        }
        
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="File not found")
    except Exception as e:
        logger.error(f"Delete error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/cleanup")
async def cleanup_old_files(days_old: int = 7):
    """
    Clean up files older than specified days.
    
    Args:
        days_old: Delete files older than this many days
    
    Returns:
        Cleanup summary
    """
    try:
        deleted_count = await storage_service.cleanup_old_files(days_old)
        
        return {
            "message": f"Cleanup completed",
            "deleted_files": deleted_count,
            "days_old": days_old
        }
        
    except Exception as e:
        logger.error(f"Cleanup error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))