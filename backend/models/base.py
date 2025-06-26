# backend/models/base.py
"""
Base Pydantic models for the Azure Cognitive Services API.
"""
from typing import Optional, Dict, Any, List, Union, Literal
from datetime import datetime
from enum import Enum
from pydantic import BaseModel, Field, validator
import uuid


class ServiceType(str, Enum):
    """Supported service types."""
    DOCUMENT_INTELLIGENCE = "document_intelligence"
    TRANSLATION = "translation"
    TRANSCRIPTION = "transcription"


class JobStatus(str, Enum):
    """Job processing status."""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    TIMEOUT = "timeout"


class ErrorSeverity(str, Enum):
    """Error severity levels."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class BaseJobModel(BaseModel):
    """Base model for job-related data."""
    
    job_id: str = Field(..., description="Unique job identifier")
    service_type: ServiceType = Field(..., description="Type of service being used")
    status: JobStatus = Field(default=JobStatus.PENDING, description="Current job status")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Job creation timestamp")
    updated_at: datetime = Field(default_factory=datetime.utcnow, description="Last update timestamp")
    
    @validator('job_id')
    def validate_job_id(cls, v):
        """Validate job ID format."""
        if not v:
            raise ValueError("Job ID cannot be empty")
        if len(v) > 64:
            raise ValueError("Job ID too long")
        return v
    
    class Config:
        use_enum_values = True
        json_encoders = {
            datetime: lambda v: v.isoformat() if v else None
        }


class FileMetadata(BaseModel):
    """File metadata model."""
    
    filename: str = Field(..., description="Original filename")
    size_bytes: int = Field(..., description="File size in bytes", ge=0)
    mime_type: str = Field(..., description="MIME type of the file")
    hash_sha256: Optional[str] = Field(None, description="SHA256 hash of file content")
    upload_timestamp: datetime = Field(default_factory=datetime.utcnow, description="Upload timestamp")
    storage_path: Optional[str] = Field(None, description="Path in storage system")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat() if v else None
        }
    
    @validator('filename')
    def validate_filename(cls, v):
        """Validate filename."""
        if not v or not v.strip():
            raise ValueError("Filename cannot be empty")
        if len(v) > 255:
            raise ValueError("Filename too long")
        return v.strip()
    
    @validator('size_bytes')
    def validate_size(cls, v):
        """Validate file size."""
        if v < 0:
            raise ValueError("File size cannot be negative")
        if v > 100 * 1024 * 1024:  # 100MB
            raise ValueError("File size too large")
        return v


class ErrorDetails(BaseModel):
    """Error details model."""
    
    error_code: str = Field(..., description="Error code")
    error_message: str = Field(..., description="Human-readable error message")
    severity: ErrorSeverity = Field(default=ErrorSeverity.MEDIUM, description="Error severity")
    details: Dict[str, Any] = Field(default_factory=dict, description="Additional error details")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Error timestamp")
    retry_possible: bool = Field(default=False, description="Whether the operation can be retried")
    retry_after: Optional[int] = Field(None, description="Suggested retry delay in seconds")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat() if v else None
        }


class ProcessingProgress(BaseModel):
    """Processing progress model."""
    
    current_step: str = Field(..., description="Current processing step")
    progress_percentage: int = Field(..., description="Progress percentage (0-100)", ge=0, le=100)
    estimated_completion_time: Optional[datetime] = Field(None, description="Estimated completion time")
    message: Optional[str] = Field(None, description="Progress message")
    started_at: datetime = Field(default_factory=datetime.utcnow, description="Processing start time")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat() if v else None
        }


class CostEstimate(BaseModel):
    """Cost estimation model."""
    
    service_type: ServiceType = Field(..., description="Service type")
    estimated_cost_usd: float = Field(..., description="Estimated cost in USD", ge=0)
    cost_breakdown: Dict[str, float] = Field(default_factory=dict, description="Cost breakdown by component")
    billing_units: Dict[str, Union[int, float]] = Field(default_factory=dict, description="Billing units used")
    confidence: str = Field(default="medium", description="Confidence level of estimate")
    calculated_at: datetime = Field(default_factory=datetime.utcnow, description="Calculation timestamp")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat() if v else None
        }
    
    @validator('estimated_cost_usd')
    def validate_cost(cls, v):
        """Validate cost value."""
        if v < 0:
            raise ValueError("Cost cannot be negative")
        if v > 1000:  # Sanity check
            raise ValueError("Cost estimate seems too high")
        return round(v, 4)  # Round to 4 decimal places


class WebSocketMessage(BaseModel):
    """WebSocket message model."""
    
    type: str = Field(..., description="Message type")
    job_id: Optional[str] = Field(None, description="Related job ID")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Message timestamp")
    data: Dict[str, Any] = Field(default_factory=dict, description="Message data")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat() if v else None
        }


class JobUpdateMessage(WebSocketMessage):
    """Job update WebSocket message."""
    
    type: Literal["job_update"] = Field(default="job_update")
    job_id: str = Field(..., description="Job ID")
    status: JobStatus = Field(..., description="Current job status")
    progress: Optional[ProcessingProgress] = Field(None, description="Processing progress")
    error: Optional[ErrorDetails] = Field(None, description="Error details if failed")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat() if v else None
        }


class ErrorMessage(WebSocketMessage):
    """Error WebSocket message."""
    
    type: Literal["error"] = Field(default="error")
    error: ErrorDetails = Field(..., description="Error details")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat() if v else None
        }


class CompletionMessage(WebSocketMessage):
    """Job completion WebSocket message."""
    
    type: Literal["job_completed"] = Field(default="job_completed")
    job_id: str = Field(..., description="Job ID")
    results_url: Optional[str] = Field(None, description="URL to download results")
    final_cost: Optional[float] = Field(None, description="Final processing cost")
    processing_time_seconds: Optional[float] = Field(None, description="Total processing time")
    data: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Additional completion data")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat() if v else None
        }


class APIResponse(BaseModel):
    """Standard API response model."""
    
    success: bool = Field(..., description="Whether the request was successful")
    message: Optional[str] = Field(None, description="Response message")
    data: Optional[Dict[str, Any]] = Field(None, description="Response data")
    error: Optional[ErrorDetails] = Field(None, description="Error details if unsuccessful")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Response timestamp")
    correlation_id: Optional[str] = Field(None, description="Request correlation ID")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat() if v else None
        }


class PaginatedResponse(BaseModel):
    """Paginated response model."""
    
    items: List[Dict[str, Any]] = Field(..., description="Response items")
    total_count: int = Field(..., description="Total number of items", ge=0)
    page: int = Field(..., description="Current page number", ge=1)
    page_size: int = Field(..., description="Number of items per page", ge=1, le=100)
    total_pages: int = Field(..., description="Total number of pages", ge=0)
    has_next: bool = Field(..., description="Whether there is a next page")
    has_previous: bool = Field(..., description="Whether there is a previous page")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat() if v else None
        }


class HealthStatus(BaseModel):
    """Health check status model."""
    
    status: str = Field(..., description="Overall health status")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Health check timestamp")
    services: Dict[str, bool] = Field(default_factory=dict, description="Individual service health")
    version: Optional[str] = Field(None, description="Application version")
    uptime_seconds: Optional[float] = Field(None, description="Application uptime in seconds")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat() if v else None
        }


def generate_job_id(service_type: ServiceType) -> str:
    """Generate a unique job ID."""
    prefix_map = {
        ServiceType.DOCUMENT_INTELLIGENCE: "doc",
        ServiceType.TRANSLATION: "trans",
        ServiceType.TRANSCRIPTION: "speech"
    }
    
    prefix = prefix_map.get(service_type, "job")
    unique_id = str(uuid.uuid4()).replace("-", "")[:12]
    timestamp = int(datetime.utcnow().timestamp())
    
    return f"{prefix}-{timestamp}-{unique_id}"


def create_error_response(
    error_code: str,
    error_message: str,
    details: Dict[str, Any] = None,
    correlation_id: str = None
) -> APIResponse:
    """Create a standardized error response."""
    error_details = ErrorDetails(
        error_code=error_code,
        error_message=error_message,
        details=details or {}
    )
    
    return APIResponse(
        success=False,
        error=error_details,
        correlation_id=correlation_id
    )


def create_success_response(
    data: Dict[str, Any] = None,
    message: str = None,
    correlation_id: str = None
) -> APIResponse:
    """Create a standardized success response."""
    return APIResponse(
        success=True,
        message=message,
        data=data or {},
        correlation_id=correlation_id
    )