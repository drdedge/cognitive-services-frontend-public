"""
Infrastructure validation tests to ensure the test setup works correctly.
These tests validate the testing framework itself and sample data.
"""
import pytest
import asyncio
from pathlib import Path
import json
import tempfile
from unittest.mock import Mock, AsyncMock

# Import our test fixtures and utilities
from fixtures.sample_data import get_sample_data, SAMPLE_DOCUMENT_ANALYSIS
from fixtures.azure_mocks import create_azure_mocks, MockDocumentIntelligenceClient


class TestInfrastructure:
    """Test the testing infrastructure itself."""
    
    def test_pytest_configuration(self):
        """Test that pytest is configured correctly."""
        # This test should always pass to validate basic pytest setup
        assert True
    
    def test_async_support(self):
        """Test that async test support is working."""
        async def async_function():
            await asyncio.sleep(0.001)
            return "async_result"
        
        # Test that we can run async functions
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            result = loop.run_until_complete(async_function())
            assert result == "async_result"
        finally:
            loop.close()
    
    @pytest.mark.asyncio
    async def test_async_pytest_decorator(self):
        """Test that @pytest.mark.asyncio works correctly."""
        await asyncio.sleep(0.001)
        assert True
    
    def test_sample_data_loading(self):
        """Test that sample data can be loaded correctly."""
        # Test basic sample data access
        doc_analysis = get_sample_data("document_analysis")
        assert doc_analysis is not None
        assert "job_id" in doc_analysis
        assert "status" in doc_analysis
        
        # Test specific scenario data
        error_data = get_sample_data("errors", "file_too_large")
        assert error_data is not None
        assert error_data["error_code"] == "FILE_SIZE_EXCEEDED"
    
    def test_azure_mocks_creation(self):
        """Test that Azure service mocks can be created."""
        # Test creating multiple service mocks
        mocks = create_azure_mocks(
            services=["document_intelligence", "translator", "blob_storage"],
            scenarios={"document_intelligence": "success", "translator": "auto_detect"}
        )
        
        assert "document_intelligence" in mocks
        assert "translator" in mocks
        assert "blob_storage" in mocks
        
        # Test mock functionality
        doc_client = mocks["document_intelligence"]
        assert isinstance(doc_client, MockDocumentIntelligenceClient)
        assert doc_client.scenario == "success"
    
    def test_temporary_directory_fixture(self, temp_upload_dir):
        """Test that temporary directory fixture works."""
        assert temp_upload_dir.exists()
        assert temp_upload_dir.is_dir()
        
        # Test file creation in temp directory
        test_file = temp_upload_dir / "test.txt"
        test_file.write_text("test content")
        assert test_file.exists()
        assert test_file.read_text() == "test content"
    
    def test_sample_files_fixture(self, sample_files):
        """Test that sample files fixture creates test files."""
        expected_types = ["pdf", "docx", "wav", "mp3", "txt"]
        
        for file_type in expected_types:
            assert file_type in sample_files
            assert sample_files[file_type].exists()
            assert sample_files[file_type].stat().st_size > 0
    
    def test_mock_azure_storage_fixture(self, mock_azure_storage):
        """Test that Azure storage mock fixture works."""
        assert mock_azure_storage is not None
        assert hasattr(mock_azure_storage, "blob_service_client")
        
        # Test mock chain
        container_client = mock_azure_storage.blob_service_client.get_container_client("test")
        blob_client = container_client.get_blob_client("test.pdf")
        assert blob_client is not None
    
    def test_environment_variables_fixture(self, mock_env_vars):
        """Test that environment variables are set correctly."""
        required_vars = [
            "AZURE_DOC_INTELLIGENCE_ENDPOINT",
            "AZURE_DOC_INTELLIGENCE_KEY",
            "AZURE_TRANSLATOR_ENDPOINT",
            "AZURE_TRANSLATOR_KEY",
            "AZURE_SPEECH_ENDPOINT",
            "AZURE_SPEECH_KEY",
            "AZURE_STORAGE_CONNECTION_STRING",
            "AZURE_STORAGE_CONTAINER"
        ]
        
        for var in required_vars:
            assert var in mock_env_vars
            assert mock_env_vars[var] is not None


class TestSampleDataValidation:
    """Validate the structure and content of sample test data."""
    
    def test_document_analysis_structure(self):
        """Test document analysis sample data structure."""
        data = SAMPLE_DOCUMENT_ANALYSIS
        
        # Required top-level fields
        required_fields = ["job_id", "status", "confidence", "pages", "tables", "processing_time", "cost"]
        for field in required_fields:
            assert field in data, f"Missing field: {field}"
        
        # Test pages structure
        assert len(data["pages"]) > 0
        page = data["pages"][0]
        assert "page_number" in page
        assert "text" in page
        assert "words" in page
        
        # Test words structure
        assert len(page["words"]) > 0
        word = page["words"][0]
        assert "content" in word
        assert "confidence" in word
        assert "bounding_box" in word
        
        # Test tables structure
        if data["tables"]:
            table = data["tables"][0]
            assert "table_id" in table
            assert "row_count" in table
            assert "column_count" in table
            assert "cells" in table
    
    def test_translation_sample_structure(self):
        """Test translation sample data structure."""
        data = get_sample_data("translation")
        
        required_fields = ["job_id", "source_language", "target_language", "translations"]
        for field in required_fields:
            assert field in data
        
        # Test translations structure
        assert len(data["translations"]) > 0
        translation = data["translations"][0]
        assert "original_text" in translation
        assert "translated_text" in translation
        assert "confidence" in translation
    
    def test_websocket_message_structure(self):
        """Test WebSocket message sample structure."""
        messages = get_sample_data("websocket")
        
        # Test job update message
        job_update = messages["job_update"]
        assert job_update["type"] == "job_update"
        assert "job_id" in job_update
        assert "status" in job_update
        assert "progress" in job_update
        assert "timestamp" in job_update
        
        # Test error message
        error_msg = messages["error"]
        assert error_msg["type"] == "error"
        assert "error_code" in error_msg
        assert "error_message" in error_msg
    
    def test_cost_calculation_data(self):
        """Test cost calculation sample data."""
        costs = get_sample_data("costs")
        
        # Test document intelligence costs
        doc_costs = costs["document_intelligence"]
        assert "per_page" in doc_costs
        assert "examples" in doc_costs
        assert len(doc_costs["examples"]) > 0
        
        # Test example structure
        example = doc_costs["examples"][0]
        assert "pages" in example
        assert "cost" in example


class TestMockBehavior:
    """Test that Azure service mocks behave correctly."""
    
    def test_document_intelligence_mock_success(self):
        """Test successful document intelligence mock."""
        mock_client = MockDocumentIntelligenceClient("success")
        
        # Test analyze_document method
        poller = mock_client.begin_analyze_document("prebuilt-document", b"fake pdf")
        assert poller is not None
        assert poller.done() is True
        
        result = poller.result()
        assert result.content is not None
        assert len(result.pages) > 0
    
    def test_document_intelligence_mock_table_extraction(self):
        """Test table extraction mock scenario."""
        mock_client = MockDocumentIntelligenceClient("table_extraction")
        
        poller = mock_client.begin_analyze_document("prebuilt-document", b"fake pdf")
        result = poller.result()
        
        assert len(result.tables) > 0
        table = result.tables[0]
        assert table.row_count > 0
        assert table.column_count > 0
        assert len(table.cells) > 0
    
    @pytest.mark.asyncio
    async def test_translator_mock_success(self):
        """Test successful translator mock."""
        mock_client = MockTranslatorClient("success")
        
        result = await mock_client.translate(
            text=["Hello world"],
            target_languages=["es"],
            source_language="en"
        )
        
        assert len(result) == 1
        assert "translations" in result[0]
        assert len(result[0]["translations"]) == 1
        assert result[0]["translations"][0]["to"] == "es"
    
    @pytest.mark.asyncio
    async def test_translator_mock_auto_detect(self):
        """Test auto-detection translator mock."""
        mock_client = MockTranslatorClient("auto_detect")
        
        result = await mock_client.translate(
            text=["你好"],
            target_languages=["en"]
        )
        
        assert "detectedLanguage" in result[0]
        assert result[0]["detectedLanguage"]["language"] == "zh"
    
    @pytest.mark.asyncio
    async def test_speech_service_mock_success(self):
        """Test successful speech service mock."""
        mock_client = MockSpeechServiceClient("success")
        
        result = await mock_client.recognize_once_async(Mock())
        
        assert result.text is not None
        assert result.reason == "RecognizedSpeech"
        assert "SpeechServiceResponse_JsonResult" in result.properties


@pytest.mark.performance
class TestPerformanceValidation:
    """Test that performance testing infrastructure works."""
    
    def test_timing_measurement(self):
        """Test that we can measure execution time."""
        import time
        
        start_time = time.time()
        time.sleep(0.01)  # 10ms
        duration = time.time() - start_time
        
        assert duration >= 0.01
        assert duration < 0.1  # Should be much less than 100ms
    
    @pytest.mark.slow
    def test_slow_operation_simulation(self):
        """Test handling of slow operations."""
        import time
        
        # Simulate a slow operation
        time.sleep(0.1)  # 100ms
        assert True


if __name__ == "__main__":
    # This allows running the validation tests directly
    pytest.main([__file__, "-v"])