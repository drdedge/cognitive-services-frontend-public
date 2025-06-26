# backend/tests/test_base_service.py
"""
Tests for BaseAzureService abstract base class.
"""

import pytest
from unittest.mock import Mock, patch
from typing import Dict, Any, Optional

from services.base import BaseAzureService, ProcessingResult
from models.base import ServiceType
from utils.exceptions import AzureServiceException


@pytest.mark.unit


class MockAzureService(BaseAzureService):
    """Mock implementation of BaseAzureService for testing."""
    
    def _initialize_client(self) -> None:
        """Initialize mock client."""
        self.client = Mock()
    
    async def process(
        self,
        input_data: Any,
        job_id: str,
        options: Dict[str, Any],
        progress_callback: Optional[Any] = None
    ) -> ProcessingResult:
        """Mock process implementation."""
        # Simulate progress updates
        if progress_callback:
            await self._update_progress(progress_callback, 50, "Processing...")
            await self._update_progress(progress_callback, 100, "Complete")
        
        return ProcessingResult(
            success=True,
            data={'processed': True, 'input': input_data},
            metadata={'processing_time_seconds': 1.5}
        )
    
    async def estimate_cost(self, input_metadata: Dict[str, Any]) -> Dict[str, float]:
        """Mock cost estimation."""
        return {
            'estimated_cost': 0.50,
            'base_cost': 0.40,
            'additional_cost': 0.10
        }
    
    async def validate_input(self, input_data: Any, options: Dict[str, Any]) -> bool:
        """Mock input validation."""
        return input_data is not None


class TestBaseAzureService:
    """Test suite for BaseAzureService."""
    
    def test_initialization(self):
        """Test service initialization."""
        service = MockAzureService(ServiceType.DOCUMENT_INTELLIGENCE)
        assert service.service_type == ServiceType.DOCUMENT_INTELLIGENCE
        assert service._initialized is True
        assert service.client is not None
    
    def test_initialization_failure(self):
        """Test handling of initialization failure."""
        class FailingService(BaseAzureService):
            def _initialize_client(self):
                raise Exception("Client init failed")
            
            async def process(self, *args, **kwargs):
                pass
            
            async def estimate_cost(self, *args):
                pass
            
            async def validate_input(self, *args):
                pass
        
        with pytest.raises(AzureServiceException) as exc_info:
            FailingService(ServiceType.TRANSLATION)
        
        assert "Service initialization failed" in str(exc_info.value)
    
    @pytest.mark.asyncio
    async def test_process_with_progress(self):
        """Test processing with progress callback."""
        service = MockAzureService(ServiceType.TRANSCRIPTION)
        progress_updates = []
        
        def progress_callback(percentage, message):
            progress_updates.append((percentage, message))
        
        result = await service.process(
            input_data="test data",
            job_id="test-123",
            options={},
            progress_callback=progress_callback
        )
        
        assert result.success is True
        assert result.data['processed'] is True
        assert result.processing_time == 1.5
        assert len(progress_updates) == 2
        assert progress_updates[0] == (50, "Processing...")
        assert progress_updates[1] == (100, "Complete")
    
    @pytest.mark.asyncio
    async def test_health_check(self):
        """Test health check functionality."""
        service = MockAzureService(ServiceType.TRANSLATION)
        health = await service.health_check()
        
        assert health['service'] == ServiceType.TRANSLATION.value
        assert health['healthy'] is True
        assert health['initialized'] is True
        assert 'timestamp' in health
    
    def test_handle_azure_error(self):
        """Test Azure error handling."""
        from azure.core.exceptions import ResourceNotFoundError, ClientAuthenticationError
        
        service = MockAzureService(ServiceType.DOCUMENT_INTELLIGENCE)
        
        # Test ResourceNotFoundError
        azure_error = ResourceNotFoundError("Resource not found")
        handled_error = service._handle_azure_error(azure_error)
        assert handled_error.error_code == "RESOURCE_NOT_FOUND"
        assert "resource was not found" in handled_error.message
        
        # Test ClientAuthenticationError
        auth_error = ClientAuthenticationError("Invalid key")
        handled_error = service._handle_azure_error(auth_error)
        assert handled_error.error_code == "AUTHENTICATION_FAILED"
        assert "Authentication failed" in handled_error.message
    
    def test_processing_result(self):
        """Test ProcessingResult dataclass."""
        result = ProcessingResult(
            success=True,
            data={'key': 'value'},
            metadata={'processing_time_seconds': 2.5},
            error=None
        )
        
        assert result.success is True
        assert result.data['key'] == 'value'
        assert result.processing_time == 2.5
        
        # Test with error
        error_result = ProcessingResult(
            success=False,
            data={},
            metadata={},
            error="Processing failed"
        )
        
        assert error_result.success is False
        assert error_result.error == "Processing failed"
        assert error_result.processing_time is None
    
    def test_service_info(self):
        """Test service info retrieval."""
        service = MockAzureService(ServiceType.TRANSCRIPTION)
        info = service.get_service_info()
        
        assert info['service_type'] == ServiceType.TRANSCRIPTION.value
        assert info['initialized'] is True
        assert info['has_client'] is True
        assert 'capabilities' in info
        assert info['capabilities']['async_processing'] is True