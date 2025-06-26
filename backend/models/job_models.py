"""
Job management models for the Azure Cognitive Services API.
"""
from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta
from pydantic import BaseModel, Field, validator
from .base import (
    BaseJobModel, ServiceType, JobStatus, FileMetadata, 
    ProcessingProgress, ErrorDetails, CostEstimate
)


class JobCreateRequest(BaseModel):
    """Request model for creating a new job."""
    
    service_type: ServiceType = Field(..., description="Type of service to use")
    parameters: Dict[str, Any] = Field(default_factory=dict, description="Service-specific parameters")
    priority: str = Field(default="normal", description="Job priority")
    callback_url: Optional[str] = Field(None, description="URL to receive job completion notification")
    
    @validator('priority')
    def validate_priority(cls, v):
        """Validate job priority."""
        valid_priorities = ["low", "normal", "high", "urgent"]
        if v not in valid_priorities:
            raise ValueError(f"Priority must be one of: {valid_priorities}")
        return v


class Job(BaseJobModel):
    """Complete job model."""
    
    user_id: Optional[str] = Field(None, description="User ID who created the job")
    priority: str = Field(default="normal", description="Job priority")
    parameters: Dict[str, Any] = Field(default_factory=dict, description="Service-specific parameters")
    input_files: List[FileMetadata] = Field(default_factory=list, description="Input files")
    output_files: List[FileMetadata] = Field(default_factory=list, description="Output files")
    progress: Optional[ProcessingProgress] = Field(None, description="Current processing progress")
    error: Optional[ErrorDetails] = Field(None, description="Error details if failed")
    cost_estimate: Optional[CostEstimate] = Field(None, description="Cost estimation")
    actual_cost: Optional[float] = Field(None, description="Actual processing cost")
    started_at: Optional[datetime] = Field(None, description="Processing start time")
    completed_at: Optional[datetime] = Field(None, description="Processing completion time")
    expires_at: Optional[datetime] = Field(None, description="Job expiration time")
    callback_url: Optional[str] = Field(None, description="Callback URL for notifications")
    retry_count: int = Field(default=0, description="Number of retry attempts")
    max_retries: int = Field(default=3, description="Maximum retry attempts")
    
    # New fields for transcription and other services
    results_path: Optional[str] = Field(None, description="Path to results file in storage")
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Service-specific metadata")
    
    class Config:
        use_enum_values = True
        json_encoders = {
            datetime: lambda v: v.isoformat() if v else None
        }
    
    @validator('expires_at', always=True)
    def set_expiration(cls, v, values):
        """Set default expiration time."""
        if v is None:
            created_at = values.get('created_at', datetime.utcnow())
            return created_at + timedelta(hours=24)  # Default 24 hour expiration
        return v
    
    @property
    def duration_seconds(self) -> Optional[float]:
        """Calculate job duration in seconds."""
        if self.started_at and self.completed_at:
            return (self.completed_at - self.started_at).total_seconds()
        elif self.started_at:
            return (datetime.utcnow() - self.started_at).total_seconds()
        return None
    
    @property
    def is_expired(self) -> bool:
        """Check if job has expired."""
        return self.expires_at and datetime.utcnow() > self.expires_at
    
    @property
    def can_retry(self) -> bool:
        """Check if job can be retried."""
        return (self.status == JobStatus.FAILED and 
                self.retry_count < self.max_retries and 
                not self.is_expired)


class JobSummary(BaseModel):
    """Summary view of a job."""
    
    job_id: str = Field(..., description="Job ID")
    service_type: ServiceType = Field(..., description="Service type")
    status: JobStatus = Field(..., description="Job status")
    created_at: datetime = Field(..., description="Creation timestamp")
    progress_percentage: Optional[int] = Field(None, description="Progress percentage")
    estimated_cost: Optional[float] = Field(None, description="Estimated cost")
    file_count: int = Field(default=0, description="Number of input files")
    
    class Config:
        use_enum_values = True
        json_encoders = {
            datetime: lambda v: v.isoformat() if v else None
        }


class JobListResponse(BaseModel):
    """Response model for job list endpoint."""
    
    jobs: List[JobSummary] = Field(..., description="List of jobs")
    total_count: int = Field(..., description="Total number of jobs")
    page: int = Field(..., description="Current page")
    page_size: int = Field(..., description="Page size")
    filters: Dict[str, Any] = Field(default_factory=dict, description="Applied filters")


class JobStatusUpdate(BaseModel):
    """Model for job status updates."""
    
    job_id: str = Field(..., description="Job ID")
    status: JobStatus = Field(..., description="New job status")
    progress: Optional[ProcessingProgress] = Field(None, description="Progress update")
    error: Optional[ErrorDetails] = Field(None, description="Error details")
    updated_at: datetime = Field(default_factory=datetime.utcnow, description="Update timestamp")
    
    class Config:
        use_enum_values = True
        json_encoders = {
            datetime: lambda v: v.isoformat() if v else None
        }


class JobQueue(BaseModel):
    """Job queue model."""
    
    queue_name: str = Field(..., description="Queue name")
    service_type: ServiceType = Field(..., description="Service type")
    pending_jobs: int = Field(default=0, description="Number of pending jobs")
    processing_jobs: int = Field(default=0, description="Number of processing jobs")
    max_concurrent: int = Field(default=5, description="Maximum concurrent jobs")
    average_processing_time: Optional[float] = Field(None, description="Average processing time in seconds")
    
    @property
    def is_full(self) -> bool:
        """Check if queue is at capacity."""
        return self.processing_jobs >= self.max_concurrent
    
    @property
    def estimated_wait_time(self) -> Optional[float]:
        """Estimate wait time for new jobs."""
        if self.average_processing_time and self.pending_jobs > 0:
            return self.pending_jobs * self.average_processing_time
        return None


class JobMetrics(BaseModel):
    """Job metrics model."""
    
    service_type: ServiceType = Field(..., description="Service type")
    period_start: datetime = Field(..., description="Metrics period start")
    period_end: datetime = Field(..., description="Metrics period end")
    total_jobs: int = Field(default=0, description="Total jobs in period")
    completed_jobs: int = Field(default=0, description="Successfully completed jobs")
    failed_jobs: int = Field(default=0, description="Failed jobs")
    average_processing_time: Optional[float] = Field(None, description="Average processing time")
    total_cost: Optional[float] = Field(None, description="Total cost in period")
    
    class Config:
        use_enum_values = True
        json_encoders = {
            datetime: lambda v: v.isoformat() if v else None
        }
    
    @property
    def success_rate(self) -> float:
        """Calculate success rate."""
        if self.total_jobs == 0:
            return 0.0
        return self.completed_jobs / self.total_jobs
    
    @property
    def failure_rate(self) -> float:
        """Calculate failure rate."""
        if self.total_jobs == 0:
            return 0.0
        return self.failed_jobs / self.total_jobs


class RetryPolicy(BaseModel):
    """Retry policy configuration."""
    
    max_retries: int = Field(default=3, description="Maximum retry attempts", ge=0, le=10)
    initial_delay_seconds: float = Field(default=1.0, description="Initial retry delay")
    max_delay_seconds: float = Field(default=300.0, description="Maximum retry delay")
    backoff_factor: float = Field(default=2.0, description="Backoff multiplier")
    retry_on_errors: List[str] = Field(
        default_factory=lambda: ["AZURE_SERVICE_ERROR", "NETWORK_ERROR", "TIMEOUT"],
        description="Error codes that trigger retry"
    )
    
    def get_delay(self, attempt: int) -> float:
        """Calculate delay for retry attempt."""
        delay = self.initial_delay_seconds * (self.backoff_factor ** attempt)
        return min(delay, self.max_delay_seconds)


class JobConfiguration(BaseModel):
    """Job configuration model."""
    
    service_type: ServiceType = Field(..., description="Service type")
    timeout_minutes: int = Field(default=30, description="Job timeout in minutes")
    retry_policy: RetryPolicy = Field(default_factory=RetryPolicy, description="Retry policy")
    cleanup_after_hours: int = Field(default=24, description="Hours to keep job data")
    notification_webhook: Optional[str] = Field(None, description="Webhook for notifications")
    cost_limit_usd: Optional[float] = Field(None, description="Maximum cost limit")
    
    @validator('timeout_minutes')
    def validate_timeout(cls, v):
        """Validate timeout value."""
        if v <= 0 or v > 1440:  # Max 24 hours
            raise ValueError("Timeout must be between 1 and 1440 minutes")
        return v


class JobCancellationRequest(BaseModel):
    """Request to cancel a job."""
    
    job_id: str = Field(..., description="Job ID to cancel")
    reason: Optional[str] = Field(None, description="Cancellation reason")
    force: bool = Field(default=False, description="Force cancellation even if processing")


class BulkJobOperation(BaseModel):
    """Bulk job operation request."""
    
    job_ids: List[str] = Field(..., description="List of job IDs", min_items=1, max_items=100)
    operation: str = Field(..., description="Operation to perform")
    parameters: Dict[str, Any] = Field(default_factory=dict, description="Operation parameters")
    
    @validator('operation')
    def validate_operation(cls, v):
        """Validate operation type."""
        valid_operations = ["cancel", "retry", "delete", "priority_change"]
        if v not in valid_operations:
            raise ValueError(f"Operation must be one of: {valid_operations}")
        return v


class JobSearchQuery(BaseModel):
    """Job search query model."""
    
    service_type: Optional[ServiceType] = Field(None, description="Filter by service type")
    status: Optional[JobStatus] = Field(None, description="Filter by status")
    user_id: Optional[str] = Field(None, description="Filter by user ID")
    created_after: Optional[datetime] = Field(None, description="Filter by creation date")
    created_before: Optional[datetime] = Field(None, description="Filter by creation date")
    priority: Optional[str] = Field(None, description="Filter by priority")
    page: int = Field(default=1, description="Page number", ge=1)
    page_size: int = Field(default=20, description="Page size", ge=1, le=100)
    sort_by: str = Field(default="created_at", description="Sort field")
    sort_order: str = Field(default="desc", description="Sort order")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat() if v else None
        }
    
    @validator('sort_order')
    def validate_sort_order(cls, v):
        """Validate sort order."""
        if v not in ["asc", "desc"]:
            raise ValueError("Sort order must be 'asc' or 'desc'")
        return v