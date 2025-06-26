"""
Utility modules for the Azure Cognitive Services API.
"""
from .config import get_config, load_config, validate_azure_connection
from .exceptions import (
    ServiceException, ValidationException, FileException, FileSizeException,
    UnsupportedFileFormatException, AzureServiceException, AuthenticationException,
    AuthorizationException, JobException, JobNotFoundException, JobTimeoutException,
    RateLimitException, StorageException, ConfigurationException,
    to_http_exception, handle_azure_exception
)
from .validators import (
    validate_file_size, detect_file_type, validate_file_type, validate_filename,
    validate_language_code, validate_job_id, calculate_file_hash, validate_text_length,
    validate_cost_estimate_params, sanitize_metadata
)
from .logging import (
    setup_logging, get_logger, set_correlation_id, get_correlation_id,
    log_api_request, log_api_response, log_azure_operation, log_job_event,
    log_file_operation, PerformanceTimer, time_operation
)

__all__ = [
    # Config
    'get_config', 'load_config', 'validate_azure_connection',
    
    # Exceptions
    'ServiceException', 'ValidationException', 'FileException', 'FileSizeException',
    'UnsupportedFileFormatException', 'AzureServiceException', 'AuthenticationException',
    'AuthorizationException', 'JobException', 'JobNotFoundException', 'JobTimeoutException',
    'RateLimitException', 'StorageException', 'ConfigurationException',
    'to_http_exception', 'handle_azure_exception',
    
    # Validators
    'validate_file_size', 'detect_file_type', 'validate_file_type', 'validate_filename',
    'validate_language_code', 'validate_job_id', 'calculate_file_hash', 'validate_text_length',
    'validate_cost_estimate_params', 'sanitize_metadata',
    
    # Logging
    'setup_logging', 'get_logger', 'set_correlation_id', 'get_correlation_id',
    'log_api_request', 'log_api_response', 'log_azure_operation', 'log_job_event',
    'log_file_operation', 'PerformanceTimer', 'time_operation'
]