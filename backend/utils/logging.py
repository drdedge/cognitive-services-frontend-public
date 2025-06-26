# backend/utils/logging.py
"""
Logging configuration and utilities for the Azure Cognitive Services API.
"""
import logging
import sys
import json
import uuid
import time
from typing import Dict, Any, Optional
from contextvars import ContextVar
from datetime import datetime, timezone


# Context variable for correlation ID
correlation_id_var: ContextVar[Optional[str]] = ContextVar('correlation_id', default=None)


class CorrelationFilter(logging.Filter):
    """Add correlation ID to log records."""
    
    def filter(self, record):
        correlation_id = correlation_id_var.get()
        record.correlation_id = correlation_id or 'unknown'
        return True


class ColoredFormatter(logging.Formatter):
    """Colored formatter for better readability."""
    
    # ANSI color codes
    COLORS = {
        'DEBUG': '\033[36m',    # Cyan
        'INFO': '\033[32m',     # Green
        'WARNING': '\033[33m',  # Yellow
        'ERROR': '\033[31m',    # Red
        'CRITICAL': '\033[35m', # Magenta
    }
    RESET = '\033[0m'
    BOLD = '\033[1m'
    
    def format(self, record):
        # Add color to level name
        levelname = record.levelname
        if levelname in self.COLORS:
            record.levelname = f"{self.COLORS[levelname]}{self.BOLD}{levelname}{self.RESET}"
        
        # Format the message
        message = super().format(record)
        
        # Add extra fields if present
        extras = []
        for key, value in record.__dict__.items():
            if key not in ['name', 'msg', 'args', 'levelname', 'levelno', 'pathname', 
                          'filename', 'module', 'lineno', 'funcName', 'created', 
                          'msecs', 'relativeCreated', 'thread', 'threadName', 
                          'processName', 'process', 'getMessage', 'exc_info', 
                          'exc_text', 'stack_info', 'correlation_id', 'taskName',
                          'message', 'asctime']:  # Added 'message' and 'asctime' to skip list
                # Format the extra field nicely
                if isinstance(value, dict):
                    value_str = ', '.join(f"{k}={v}" for k, v in value.items())
                else:
                    value_str = str(value)
                extras.append(f"{key}={value_str}")
        
        if extras:
            message += f" | {' | '.join(extras)}"
        
        return message


class StructuredFormatter(logging.Formatter):
    """Structured JSON formatter for logs (when needed)."""
    
    def format(self, record):
        log_entry = {
            'timestamp': datetime.fromtimestamp(record.created, tz=timezone.utc).isoformat(),
            'level': record.levelname,
            'logger': record.name,
            'message': record.getMessage(),
            'correlation_id': getattr(record, 'correlation_id', 'unknown'),
            'module': record.module,
            'function': record.funcName,
            'line': record.lineno
        }
        
        # Add exception info if present
        if record.exc_info:
            log_entry['exception'] = self.formatException(record.exc_info)
        
        # Add extra fields
        for key, value in record.__dict__.items():
            if key not in ['name', 'msg', 'args', 'levelname', 'levelno', 'pathname', 
                          'filename', 'module', 'lineno', 'funcName', 'created', 
                          'msecs', 'relativeCreated', 'thread', 'threadName', 
                          'processName', 'process', 'getMessage', 'exc_info', 
                          'exc_text', 'stack_info', 'correlation_id']:
                log_entry[key] = value
        
        return json.dumps(log_entry)


def setup_logging(level: str = "INFO", structured: bool = False) -> None:
    """
    Set up logging configuration.
    
    Args:
        level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        structured: Whether to use structured JSON logging (default: False for human-readable)
    """
    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, level.upper()))
    
    # Clear existing handlers
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
    
    # Create console handler
    handler = logging.StreamHandler(sys.stdout)
    
    if structured:
        # Use structured JSON formatter
        formatter = StructuredFormatter()
    else:
        # Use human-readable colored formatter
        formatter = ColoredFormatter(
            '%(asctime)s [%(levelname)s] %(name)s (%(correlation_id)s) - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
    
    handler.setFormatter(formatter)
    
    # Add correlation filter
    correlation_filter = CorrelationFilter()
    handler.addFilter(correlation_filter)
    
    root_logger.addHandler(handler)
    
    # Set specific logger levels to reduce noise
    logging.getLogger('azure').setLevel(logging.WARNING)
    logging.getLogger('azure.core.pipeline').setLevel(logging.WARNING)
    logging.getLogger('urllib3').setLevel(logging.WARNING)
    logging.getLogger('requests').setLevel(logging.WARNING)
    logging.getLogger('websockets').setLevel(logging.INFO)
    logging.getLogger('multipart').setLevel(logging.WARNING)


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger with the specified name.
    
    Args:
        name: Logger name
        
    Returns:
        Configured logger instance
    """
    return logging.getLogger(name)


def set_correlation_id(correlation_id: str = None) -> str:
    """
    Set correlation ID for current context.
    
    Args:
        correlation_id: Correlation ID to set (generates UUID if None)
        
    Returns:
        The correlation ID that was set
    """
    if correlation_id is None:
        correlation_id = str(uuid.uuid4())
    
    correlation_id_var.set(correlation_id)
    return correlation_id


def get_correlation_id() -> Optional[str]:
    """Get current correlation ID."""
    return correlation_id_var.get()


def log_api_request(
    logger: logging.Logger,
    method: str,
    path: str,
    query_params: Dict[str, Any] = None,
    headers: Dict[str, str] = None,
    body_size: int = None
) -> None:
    """
    Log API request details in a readable format.
    """
    # Filter sensitive headers
    safe_headers = {}
    if headers:
        sensitive_headers = ['authorization', 'x-api-key', 'cookie', 'x-ms-key']
        for key, value in headers.items():
            if any(sensitive in key.lower() for sensitive in sensitive_headers):
                safe_headers[key] = '[REDACTED]'
            else:
                safe_headers[key] = value
    
    # Build a readable message
    message = f"REQUEST {method} {path}"
    extras = {}
    
    if query_params:
        message += f" (params: {query_params})"
    
    if body_size:
        extras['size'] = f"{body_size} bytes"
    
    logger.info(message, extra=extras)


def log_api_response(
    logger: logging.Logger,
    status_code: int,
    response_time_ms: float,
    response_size: int = None,
    error_code: str = None
) -> None:
    """
    Log API response details in a readable format.
    """
    # Choose status word based on status code
    if status_code < 300:
        status_word = "SUCCESS"
    elif status_code < 400:
        status_word = "REDIRECT"
    elif status_code < 500:
        status_word = "CLIENT_ERROR"
    else:
        status_word = "SERVER_ERROR"
    
    message = f"RESPONSE {status_code} {status_word} ({response_time_ms:.1f}ms)"
    
    extras = {}
    if response_size:
        extras['size'] = f"{response_size} bytes"
    if error_code:
        extras['error'] = error_code
    
    logger.info(message, extra=extras)


def log_azure_operation(
    logger: logging.Logger,
    service: str,
    operation: str,
    duration_ms: float,
    success: bool,
    cost: float = None,
    error: str = None
) -> None:
    """
    Log Azure service operation in a readable format.
    """
    status = "SUCCESS" if success else "FAILED"
    
    message = f"Azure {service}.{operation} {status} ({duration_ms:.1f}ms)"
    
    extras = {}
    if cost is not None:
        extras['cost'] = f"${cost:.4f}"
    if error:
        extras['error'] = error
    
    level = logging.INFO if success else logging.ERROR
    logger.log(level, message, extra=extras)


def log_job_event(
    logger: logging.Logger,
    job_id: str,
    event_type: str,
    status: str = None,
    progress: int = None,
    message: str = None,
    error: str = None
) -> None:
    """
    Log job processing event in a readable format.
    """
    log_message = f"JOB {job_id}: {event_type.upper()}"
    if message:
        log_message += f" - {message}"
    
    extras = {}
    if status:
        extras['status'] = status
    if progress is not None:
        extras['progress'] = f"{progress}%"
    if error:
        extras['error'] = error
    
    level = logging.ERROR if error else logging.INFO
    logger.log(level, log_message, extra=extras)


def log_file_operation(
    logger: logging.Logger,
    operation: str,
    filename: str,
    file_size: int = None,
    mime_type: str = None,
    duration_ms: float = None,
    success: bool = True,
    error: str = None
) -> None:
    """
    Log file operation event in a readable format.
    """
    status = "SUCCESS" if success else "FAILED"
    
    message = f"FILE_{operation.upper()} {filename} {status}"
    
    extras = {}
    if file_size is not None:
        # Format file size nicely
        if file_size < 1024:
            size_str = f"{file_size}B"
        elif file_size < 1024 * 1024:
            size_str = f"{file_size / 1024:.1f}KB"
        else:
            size_str = f"{file_size / (1024 * 1024):.1f}MB"
        extras['size'] = size_str
    
    if mime_type:
        extras['type'] = mime_type
    if duration_ms is not None:
        extras['time'] = f"{duration_ms:.1f}ms"
    if error:
        extras['error'] = error
    
    level = logging.ERROR if not success else logging.INFO
    logger.log(level, message, extra=extras)


class PerformanceTimer:
    """Context manager for timing operations."""
    
    def __init__(self, logger: logging.Logger, operation: str):
        self.logger = logger
        self.operation = operation
        self.start_time = None
    
    def __enter__(self):
        self.start_time = time.time()
        # Start timing operation
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        duration = (time.time() - self.start_time) * 1000  # Convert to milliseconds
        success = exc_type is None
        
        status = "SUCCESS" if success else "FAILED"
        message = f"TIMER_END {self.operation} {status} ({duration:.1f}ms)"
        
        # Only log at INFO level if it took more than 100ms or failed
        level = logging.INFO if (duration > 100 or not success) else logging.DEBUG
        self.logger.log(level, message)


# Create a performance timer decorator
def time_operation(operation_name: str = None):
    """Decorator to time function execution."""
    def decorator(func):
        def wrapper(*args, **kwargs):
            logger = get_logger(func.__module__)
            op_name = operation_name or func.__name__
            with PerformanceTimer(logger, op_name):
                return func(*args, **kwargs)
        return wrapper
    return decorator