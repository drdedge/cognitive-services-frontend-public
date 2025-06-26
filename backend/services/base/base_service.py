# backend/services/base/base_service.py
"""
Base Azure Service Class
========================

Abstract base class for all Azure Cognitive Services implementations.
Provides common functionality for initialization, processing, error handling,
and result packaging to ensure consistency across all services.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, Callable, TypeVar, Generic
from dataclasses import dataclass
from datetime import datetime

from utils.config import get_config
from utils.logging import get_logger
from utils.exceptions import AzureServiceException
from models.base import ServiceType

logger = get_logger(__name__)

# Type for progress callbacks
ProgressCallback = Callable[[int, str], None]


@dataclass
class ProcessingResult:
    """
    Standard result container for all services.
    
    Attributes:
        success: Whether processing completed successfully
        data: Service-specific result data
        metadata: Processing metadata (duration, stats, etc.)
        error: Error details if processing failed
    """
    success: bool
    data: Dict[str, Any]
    metadata: Dict[str, Any]
    error: Optional[str] = None
    
    @property
    def processing_time(self) -> Optional[float]:
        """Get processing time from metadata if available."""
        return self.metadata.get('processing_time_seconds')


class BaseAzureService(ABC):
    """
    Abstract base class for all Azure Cognitive Services.
    
    Provides common functionality:
    - Configuration management
    - Client initialization
    - Error handling
    - Progress callbacks
    - Cost estimation interface
    - Health checking
    """
    
    def __init__(self, service_type: ServiceType):
        """
        Initialize base service.
        
        Args:
            service_type: Type of Azure service
        """
        self.service_type = service_type
        self.config = get_config()
        self.client = None
        self._initialized = False
        
        # Initialize the Azure client
        try:
            self._initialize_client()
            self._initialized = True
            logger.info(f"{service_type.value} service initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize {service_type.value} service: {e}")
            raise AzureServiceException(
                message=f"Service initialization failed: {str(e)}",
                service=service_type.value
            )
    
    @abstractmethod
    def _initialize_client(self) -> None:
        """
        Initialize the Azure service client.
        Must be implemented by each service.
        """
        pass
    
    @abstractmethod
    async def process(
        self,
        input_data: Any,
        job_id: str,
        options: Dict[str, Any],
        progress_callback: Optional[ProgressCallback] = None
    ) -> ProcessingResult:
        """
        Main processing method that all services must implement.
        
        Args:
            input_data: Input to process (file path, text, etc.)
            job_id: Unique job identifier
            options: Service-specific processing options
            progress_callback: Optional callback for progress updates
            
        Returns:
            ProcessingResult with service-specific data
        """
        pass
    
    @abstractmethod
    async def estimate_cost(
        self,
        input_metadata: Dict[str, Any]
    ) -> Dict[str, float]:
        """
        Estimate processing cost based on input metadata.
        
        Args:
            input_metadata: Information about input (size, type, etc.)
            
        Returns:
            Dictionary with cost breakdown
        """
        pass
    
    @abstractmethod
    async def validate_input(
        self,
        input_data: Any,
        options: Dict[str, Any]
    ) -> bool:
        """
        Validate input before processing.
        
        Args:
            input_data: Input to validate
            options: Processing options
            
        Returns:
            True if input is valid
            
        Raises:
            ValidationException: If input is invalid
        """
        pass
    
    async def health_check(self) -> Dict[str, Any]:
        """
        Check if service is healthy and operational.
        
        Returns:
            Health status dictionary
        """
        return {
            'service': self.service_type.value,
            'healthy': self._initialized and self.client is not None,
            'initialized': self._initialized,
            'timestamp': datetime.utcnow().isoformat()
        }
    
    def _handle_azure_error(self, error: Exception) -> AzureServiceException:
        """
        Convert Azure SDK errors to our custom exceptions.
        
        Args:
            error: Azure SDK exception
            
        Returns:
            AzureServiceException with appropriate details
        """
        from azure.core.exceptions import (
            ResourceNotFoundError,
            ClientAuthenticationError,
            HttpResponseError
        )
        
        error_message = str(error)
        error_code = "AZURE_ERROR"
        
        if isinstance(error, ResourceNotFoundError):
            error_code = "RESOURCE_NOT_FOUND"
            error_message = "The requested resource was not found"
        elif isinstance(error, ClientAuthenticationError):
            error_code = "AUTHENTICATION_FAILED"
            error_message = "Authentication failed. Check your API keys"
        elif isinstance(error, HttpResponseError):
            error_code = f"HTTP_ERROR_{error.status_code}"
            error_message = f"Azure API error: {error.message}"
        
        return AzureServiceException(
            message=error_message,
            service=self.service_type.value,
            error_code=error_code,
            azure_error=error
        )
    
    async def _update_progress(
        self,
        progress_callback: Optional[ProgressCallback],
        percentage: int,
        message: str
    ) -> None:
        """
        Helper to safely call progress callback.
        
        Args:
            progress_callback: Callback function
            percentage: Progress percentage (0-100)
            message: Progress message
        """
        if progress_callback:
            try:
                # Handle both sync and async callbacks
                import asyncio
                if asyncio.iscoroutinefunction(progress_callback):
                    await progress_callback(percentage, message)
                else:
                    progress_callback(percentage, message)
            except Exception as e:
                logger.warning(f"Progress callback error: {e}")
    
    def get_service_info(self) -> Dict[str, Any]:
        """
        Get service information and capabilities.
        
        Returns:
            Service information dictionary
        """
        return {
            'service_type': self.service_type.value,
            'initialized': self._initialized,
            'has_client': self.client is not None,
            'capabilities': self._get_capabilities()
        }
    
    def _get_capabilities(self) -> Dict[str, bool]:
        """
        Get service-specific capabilities.
        Override in subclasses to provide specific capabilities.
        
        Returns:
            Dictionary of capability flags
        """
        return {
            'batch_processing': False,
            'streaming': False,
            'async_processing': True
        }