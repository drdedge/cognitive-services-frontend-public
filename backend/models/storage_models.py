# backend/models/storage_models.py
"""
Storage data models
===================
"""

from typing import List, Optional, Dict
from datetime import datetime
from pydantic import BaseModel, Field


class FileMetadata(BaseModel):
    """File metadata model."""
    name: str
    path: str
    size: int
    content_type: str
    created_at: datetime
    modified_at: datetime
    url: Optional[str] = None
    tags: Dict[str, str] = Field(default_factory=dict)
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat() if v else None
        }


class FileUploadResponse(BaseModel):
    """Response model for file upload."""
    file_name: str
    file_path: str
    size: int
    content_type: str
    url: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat() if v else None
        }


class FileListResponse(BaseModel):
    """Response model for file listing."""
    files: List[FileMetadata]
    total: int
    has_more: bool = False
    next_marker: Optional[str] = None