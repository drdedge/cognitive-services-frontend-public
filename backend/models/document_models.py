# backend/models/document_models.py
"""
Document Intelligence data models
=================================
"""

from enum import Enum
from typing import List, Dict, Optional, Any
from datetime import datetime
from pydantic import BaseModel, Field


class ProcessingStatus(str, Enum):
    """Document processing status enumeration."""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class DocumentProcessingRequest(BaseModel):
    """Request model for document processing."""
    extract_tables: bool = True
    extract_text: bool = True
    output_format: str = Field(default="markdown", pattern="^(markdown|json)$")
    enable_ocr: bool = True


class TableData(BaseModel):
    """Extracted table data model."""
    page_number: int
    table_index: int
    rows: int
    columns: int
    cells: List[List[str]]
    confidence: Optional[float] = None


class PageData(BaseModel):
    """Page data model."""
    page_number: int
    width: float
    height: float
    text_angle: float
    words: List[Dict[str, Any]]
    tables: List[TableData]


class DocumentProcessingResponse(BaseModel):
    """Response model for document processing."""
    task_id: str
    status: ProcessingStatus
    message: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = None
    results: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat() if v else None
        }


class DocumentResults(BaseModel):
    """Document processing results."""
    document_name: str
    total_pages: int
    extracted_tables: List[TableData]
    markdown_content: Optional[str] = None
    confidence_stats: Dict[str, Any]
    csv_files: List[str]
    excel_file: Optional[str] = None
    confidence_dashboard: Optional[str] = None
    md_pages: List[str] = []
    processing_time_seconds: float
    azure_response_json: Optional[str] = None