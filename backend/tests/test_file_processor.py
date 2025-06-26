# backend/tests/test_file_processor.py
"""
Tests for FileProcessor shared utility.
"""

import pytest
import os
import tempfile
from unittest.mock import Mock, AsyncMock, patch
from io import BytesIO

from services.shared import FileProcessor
from models.base import ServiceType


@pytest.mark.unit


class TestFileProcessor:
    """Test suite for FileProcessor."""
    
    @pytest.fixture
    def mock_file_handler(self):
        """Mock file handler."""
        with patch('services.shared.file_processor.get_file_handler') as mock:
            handler = Mock()
            handler.zip_files = AsyncMock(return_value="/tmp/test_results.zip")
            mock.return_value = handler
            yield handler
    
    @pytest.fixture
    def mock_storage_service(self):
        """Mock storage service."""
        with patch('services.shared.file_processor.get_storage_service') as mock:
            service = Mock()
            service.upload_file_from_path = AsyncMock()
            service.download_to_path = AsyncMock()
            service.list_blobs = AsyncMock(return_value=[
                {'name': 'test/job1/file1.txt'},
                {'name': 'test/job1/file2.txt'}
            ])
            service.delete_blob = AsyncMock()
            service.get_blob_properties = AsyncMock(return_value={'size': 1024})
            mock.return_value = service
            yield service
    
    @pytest.fixture
    def file_processor(self, mock_file_handler, mock_storage_service):
        """Create FileProcessor with mocked dependencies."""
        return FileProcessor()
    
    @pytest.fixture
    def mock_upload_file(self):
        """Create a mock UploadFile."""
        file = Mock()
        file.filename = "test_document.pdf"
        file.read = AsyncMock(return_value=b"test file content")
        return file
    
    @pytest.mark.asyncio
    async def test_save_upload_file(self, file_processor, mock_upload_file, mock_storage_service):
        """Test saving an uploaded file."""
        job_id = "test-123"
        service_type = ServiceType.DOCUMENT_INTELLIGENCE
        
        result = await file_processor.save_upload_file(
            mock_upload_file,
            job_id,
            service_type
        )
        
        # Verify result
        assert result['filename'] == "test_document.pdf"
        assert result['size'] == 17  # len(b"test file content")
        assert 'local_path' in result
        assert 'blob_path' in result
        
        # Verify blob upload was called
        expected_blob_path = f"{service_type.value}/{job_id}/input/test_document.pdf"
        mock_storage_service.upload_file_from_path.assert_called_once()
        call_args = mock_storage_service.upload_file_from_path.call_args[0]
        assert call_args[1] == expected_blob_path
        
        # Cleanup temp file
        if os.path.exists(result['local_path']):
            os.remove(result['local_path'])
    
    @pytest.mark.asyncio
    async def test_download_from_blob(self, file_processor, mock_storage_service):
        """Test downloading from blob storage."""
        blob_path = "test/job1/results.zip"
        
        # Mock the download
        async def mock_download(blob_path, local_path):
            # Create the file to simulate download
            with open(local_path, 'w') as f:
                f.write("downloaded content")
        
        mock_storage_service.download_to_path.side_effect = mock_download
        
        # Download file
        local_path = await file_processor.download_from_blob(blob_path)
        
        # Verify download was called
        mock_storage_service.download_to_path.assert_called_once()
        assert os.path.exists(local_path)
        
        # Cleanup
        if os.path.exists(local_path):
            os.remove(local_path)
    
    @pytest.mark.asyncio
    async def test_create_results_zip(self, file_processor, mock_file_handler, mock_storage_service):
        """Test creating results ZIP."""
        job_id = "test-456"
        service_type = ServiceType.TRANSLATION
        
        # Create temp files to zip
        temp_files = []
        for i in range(3):
            fd, path = tempfile.mkstemp()
            os.write(fd, f"content {i}".encode())
            os.close(fd)
            temp_files.append(path)
        
        try:
            # Create ZIP
            blob_path = await file_processor.create_results_zip(
                job_id,
                temp_files,
                service_type,
                metadata={'test': 'metadata'}
            )
            
            # Verify file handler zip was called
            mock_file_handler.zip_files.assert_called_once_with(
                temp_files,
                f"{job_id}_results.zip",
                job_id
            )
            
            # Verify upload was called
            expected_blob_path = f"{service_type.value}/{job_id}/results/{job_id}_results.zip"
            assert blob_path == expected_blob_path
            mock_storage_service.upload_file_from_path.assert_called()
            
        finally:
            # Cleanup temp files
            for path in temp_files:
                if os.path.exists(path):
                    os.remove(path)
    
    @pytest.mark.asyncio
    async def test_cleanup_job_files(self, file_processor, mock_storage_service):
        """Test cleaning up job files."""
        job_id = "test-789"
        service_type = ServiceType.TRANSCRIPTION
        
        # Cleanup files
        deleted_count = await file_processor.cleanup_job_files(job_id, service_type)
        
        # Verify operations
        expected_prefix = f"{service_type.value}/{job_id}/"
        mock_storage_service.list_blobs.assert_called_once_with(expected_prefix)
        assert mock_storage_service.delete_blob.call_count == 2
        assert deleted_count == 2
    
    def test_cleanup_temp_file(self, file_processor):
        """Test cleaning up temporary file."""
        # Create a temp file
        fd, temp_path = tempfile.mkstemp()
        os.close(fd)
        
        # Verify file exists
        assert os.path.exists(temp_path)
        
        # Clean it up
        file_processor.cleanup_temp_file(temp_path)
        
        # Verify it's gone
        assert not os.path.exists(temp_path)
    
    @pytest.mark.asyncio
    async def test_file_exists(self, file_processor, mock_storage_service):
        """Test checking if file exists."""
        # Test existing file
        exists = await file_processor.file_exists("test/exists.txt")
        assert exists is True
        
        # Test non-existing file
        mock_storage_service.get_blob_properties.side_effect = Exception("Not found")
        exists = await file_processor.file_exists("test/not-exists.txt")
        assert exists is False