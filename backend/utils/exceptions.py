"""
Custom exception classes for the Azure Cognitive Services API.
"""
from typing import Optional, Dict, Any
from fastapi import HTTPException


class ServiceException(Exception):
    """Base exception for service-level errors."""
    
    def __init__(
        self,
        message: str,
        error_code: str = "SERVICE_ERROR",
        details: Optional[Dict[str, Any]] = None,
        status_code: int = 500
    ):
        self.message = message
        self.error_code = error_code
        self.details = details or {}
        self.status_code = status_code
        super().__init__(message)


class ValidationException(ServiceException):
    """Exception for input validation errors."""
    
    def __init__(self, message: str, field: str = None, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            error_code="VALIDATION_ERROR",
            details={"field": field, **(details or {})},
            status_code=422
        )


class FileException(ServiceException):
    """Exception for file-related errors."""
    
    def __init__(self, message: str, error_code: str = "FILE_ERROR", details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            error_code=error_code,
            details=details,
            status_code=400
        )


class FileSizeException(FileException):
    """Exception for file size validation errors."""
    
    def __init__(self, file_size: int, max_size: int):
        super().__init__(
            message=f"File size {file_size} bytes exceeds maximum limit of {max_size} bytes",
            error_code="FILE_SIZE_EXCEEDED",
            details={
                "file_size": file_size,
                "max_size": max_size,
                "max_size_mb": max_size // (1024 * 1024)
            }
        )


class UnsupportedFileFormatException(FileException):
    """Exception for unsupported file format errors."""
    
    def __init__(self, detected_format: str, supported_formats: list):
        super().__init__(
            message=f"File format '{detected_format}' is not supported",
            error_code="UNSUPPORTED_FILE_FORMAT",
            details={
                "detected_format": detected_format,
                "supported_formats": supported_formats
            }
        )


class AzureServiceException(ServiceException):
    """Exception for Azure service errors."""
    
    def __init__(
        self,
        message: str,
        service: str,
        azure_error: Optional[Exception] = None,
        retry_after: Optional[int] = None
    ):
        details = {"service": service}
        if azure_error:
            details["azure_error"] = str(azure_error)
            details["azure_error_type"] = type(azure_error).__name__
        if retry_after:
            details["retry_after"] = retry_after
        
        super().__init__(
            message=message,
            error_code="AZURE_SERVICE_ERROR",
            details=details,
            status_code=502
        )


class AuthenticationException(ServiceException):
    """Exception for authentication errors."""
    
    def __init__(self, message: str = "Authentication failed"):
        super().__init__(
            message=message,
            error_code="AUTHENTICATION_FAILED",
            status_code=401
        )


class AuthorizationException(ServiceException):
    """Exception for authorization errors."""
    
    def __init__(self, message: str = "Access denied"):
        super().__init__(
            message=message,
            error_code="AUTHORIZATION_FAILED",
            status_code=403
        )


class JobException(ServiceException):
    """Exception for job processing errors."""
    
    def __init__(
        self,
        message: str,
        job_id: str,
        error_code: str = "JOB_ERROR",
        details: Optional[Dict[str, Any]] = None
    ):
        job_details = {"job_id": job_id, **(details or {})}
        super().__init__(
            message=message,
            error_code=error_code,
            details=job_details,
            status_code=400
        )


class JobNotFoundException(JobException):
    """Exception for job not found errors."""
    
    def __init__(self, job_id: str):
        super().__init__(
            message=f"Job {job_id} not found",
            job_id=job_id,
            error_code="JOB_NOT_FOUND"
        )
        self.status_code = 404


class JobTimeoutException(JobException):
    """Exception for job timeout errors."""
    
    def __init__(self, job_id: str, timeout_seconds: int):
        super().__init__(
            message=f"Job {job_id} timed out after {timeout_seconds} seconds",
            job_id=job_id,
            error_code="JOB_TIMEOUT",
            details={"timeout_seconds": timeout_seconds}
        )


class RateLimitException(ServiceException):
    """Exception for rate limiting errors."""
    
    def __init__(self, retry_after: int = 60):
        super().__init__(
            message=f"Rate limit exceeded. Retry after {retry_after} seconds",
            error_code="RATE_LIMIT_EXCEEDED",
            details={"retry_after": retry_after},
            status_code=429
        )


class StorageException(ServiceException):
    """Exception for storage-related errors."""
    
    def __init__(
        self,
        message: str,
        operation: str,
        error_code: str = "STORAGE_ERROR",
        details: Optional[Dict[str, Any]] = None
    ):
        storage_details = {"operation": operation, **(details or {})}
        super().__init__(
            message=message,
            error_code=error_code,
            details=storage_details,
            status_code=500
        )


class DocumentProcessingException(ServiceException):
    """Exception for document processing errors."""
    
    def __init__(
        self,
        message: str,
        job_id: str = None,
        file_path: str = None,
        error_code: str = "DOCUMENT_PROCESSING_ERROR",
        details: Optional[Dict[str, Any]] = None
    ):
        processing_details = {}
        if job_id:
            processing_details["job_id"] = job_id
        if file_path:
            processing_details["file_path"] = file_path
        processing_details.update(details or {})
        
        super().__init__(
            message=message,
            error_code=error_code,
            details=processing_details,
            status_code=500
        )


class TranscriptionException(ServiceException):
    """Exception for transcription errors."""
    
    def __init__(
        self,
        message: str,
        job_id: str = None,
        details: Optional[Dict[str, Any]] = None
    ):
        error_details = {}
        if job_id:
            error_details["job_id"] = job_id
        error_details.update(details or {})
        
        super().__init__(
            message=message,
            error_code="TRANSCRIPTION_ERROR",
            details=error_details,
            status_code=400
        )


class ConfigurationException(ServiceException):
    """Exception for configuration errors."""
    
    def __init__(self, message: str, setting: str = None):
        super().__init__(
            message=message,
            error_code="CONFIGURATION_ERROR",
            details={"setting": setting} if setting else {},
            status_code=500
        )


def to_http_exception(exc: ServiceException) -> HTTPException:
    """Convert a ServiceException to FastAPI HTTPException."""
    return HTTPException(
        status_code=exc.status_code,
        detail={
            "error_code": exc.error_code,
            "message": exc.message,
            "details": exc.details
        }
    )


def handle_azure_exception(exc: Exception, service: str) -> AzureServiceException:
    """Convert Azure SDK exceptions to AzureServiceException."""
    # Handle specific Azure exception types
    if hasattr(exc, 'status_code'):
        if exc.status_code == 401:
            return AzureServiceException(
                message=f"Authentication failed for {service}",
                service=service,
                azure_error=exc
            )
        elif exc.status_code == 403:
            return AzureServiceException(
                message=f"Access denied for {service}",
                service=service,
                azure_error=exc
            )
        elif exc.status_code == 429:
            retry_after = getattr(exc, 'retry_after', 60)
            return AzureServiceException(
                message=f"Rate limit exceeded for {service}",
                service=service,
                azure_error=exc,
                retry_after=retry_after
            )
        elif exc.status_code >= 500:
            return AzureServiceException(
                message=f"{service} service temporarily unavailable",
                service=service,
                azure_error=exc
            )
    
    # Handle network/connection errors
    if "connection" in str(exc).lower() or "network" in str(exc).lower():
        return AzureServiceException(
            message=f"Connection failed to {service}",
            service=service,
            azure_error=exc
        )
    
    # Generic Azure service error
    return AzureServiceException(
        message=f"Error communicating with {service}: {str(exc)}",
        service=service,
        azure_error=exc
    )