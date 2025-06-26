"""
Tests for the base ResultPackager class.

Tests the core functionality that all service packagers inherit including
directory structure creation, file operations, and ZIP packaging.
"""
import os
import json
import tempfile
import zipfile
from pathlib import Path
from unittest.mock import Mock, AsyncMock, patch, MagicMock
import pytest

from services.shared.result_packager import ResultPackager
from utils.file_handler import FileHandler


class ConcreteResultPackager(ResultPackager):
    """Concrete implementation for testing abstract base class."""
    
    @property
    def service_name(self) -> str:
        return "test_service"
    
    async def _package_service_results(self, temp_dir, results, original_filename, metadata):
        """Simple implementation for testing."""
        files = []
        
        # Create a test file
        test_file_path = os.path.join(temp_dir, "processed", "test_output.txt")
        file_info = await self._save_text_file(
            "Test content",
            test_file_path,
            "Test file"
        )
        files.append(file_info)
        
        return {
            "files_count": len(files),
            "files": files,
            "test_stat": 123
        }


class TestResultPackagerBase:
    """Test suite for base ResultPackager functionality."""
    
    @pytest.fixture
    def mock_file_handler(self):
        """Create mock FileHandler."""
        handler = Mock(spec=FileHandler)
        handler.upload_to_blob = AsyncMock(return_value="https://test.blob.core.windows.net/test.zip")
        return handler
    
    @pytest.fixture
    def packager(self, mock_file_handler):
        """Create test packager instance."""
        return ConcreteResultPackager(mock_file_handler)
    
    @pytest.mark.asyncio
    async def test_standard_structure_creation(self, packager):
        """Test that standard directory structure is created correctly."""
        with tempfile.TemporaryDirectory() as temp_dir:
            packager._create_standard_structure(temp_dir)
            
            # Check all standard directories exist
            assert os.path.exists(os.path.join(temp_dir, "original"))
            assert os.path.exists(os.path.join(temp_dir, "processed"))
            assert os.path.exists(os.path.join(temp_dir, "metadata"))
            assert os.path.exists(os.path.join(temp_dir, "reports"))
    
    @pytest.mark.asyncio
    async def test_summary_json_format(self, packager):
        """Test summary.json has all required fields."""
        job_id = "test-job-123"
        original_filename = "test_document.pdf"
        package_stats = {
            "files_count": 5,
            "test_metric": 100,
            "files": [
                {"path": "file1.txt", "type": "text", "description": "Test file"}
            ]
        }
        metadata = {"user": "test_user", "options": {"lang": "en"}}
        
        summary = packager._create_summary_json(
            job_id, original_filename, package_stats, metadata
        )
        
        # Check required fields
        assert summary["job_id"] == job_id
        assert summary["service"] == "test_service"
        assert summary["original_filename"] == original_filename
        assert summary["package_version"] == "1.0"
        assert "processed_at" in summary
        assert summary["statistics"] == package_stats
        assert summary["metadata"] == metadata
        assert len(summary["files"]) == 1
        assert summary["files"][0]["path"] == "file1.txt"
    
    @pytest.mark.asyncio
    async def test_save_json_file(self, packager):
        """Test JSON file saving functionality."""
        with tempfile.TemporaryDirectory() as temp_dir:
            test_data = {"key": "value", "number": 42, "nested": {"inner": "data"}}
            file_path = os.path.join(temp_dir, "test.json")
            
            file_info = await packager._save_json_file(
                test_data, file_path, "Test JSON"
            )
            
            # Check file exists
            assert os.path.exists(file_path)
            
            # Check file info
            assert file_info["path"] == "test.json"
            assert file_info["type"] == "json"
            assert file_info["description"] == "Test JSON"
            assert file_info["size"] > 0
            
            # Check content
            with open(file_path, 'r') as f:
                loaded_data = json.load(f)
            assert loaded_data == test_data
    
    @pytest.mark.asyncio
    async def test_save_text_file(self, packager):
        """Test text file saving functionality."""
        with tempfile.TemporaryDirectory() as temp_dir:
            test_content = "This is test content\nWith multiple lines\n"
            file_path = os.path.join(temp_dir, "test.txt")
            
            file_info = await packager._save_text_file(
                test_content, file_path, "Test text file"
            )
            
            # Check file exists
            assert os.path.exists(file_path)
            
            # Check file info
            assert file_info["path"] == "test.txt"
            assert file_info["type"] == "text"
            assert file_info["description"] == "Test text file"
            # File size may vary slightly due to line endings (CRLF vs LF)
            assert abs(file_info["size"] - len(test_content)) <= 2
            
            # Check content
            with open(file_path, 'r') as f:
                loaded_content = f.read()
            assert loaded_content == test_content
    
    @pytest.mark.asyncio
    async def test_copy_file(self, packager):
        """Test file copying functionality."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create source file
            source_content = b"Binary test content"
            source_path = os.path.join(temp_dir, "source.bin")
            with open(source_path, 'wb') as f:
                f.write(source_content)
            
            dest_path = os.path.join(temp_dir, "dest.bin")
            
            file_info = await packager._copy_file(
                source_path, dest_path, "Copied file"
            )
            
            # Check file exists
            assert os.path.exists(dest_path)
            
            # Check file info
            assert file_info["path"] == "dest.bin"
            assert file_info["type"] == "bin"
            assert file_info["description"] == "Copied file"
            assert file_info["size"] == len(source_content)
            
            # Check content
            with open(dest_path, 'rb') as f:
                loaded_content = f.read()
            assert loaded_content == source_content
    
    @pytest.mark.asyncio
    async def test_create_package_success(self, packager, mock_file_handler):
        """Test successful package creation."""
        job_id = "test-job-456"
        results = {"test_result": "data"}
        original_filename = "input.pdf"
        metadata = {"processing_time": 10.5}
        
        download_url = await packager.create_package(
            job_id, results, original_filename, metadata
        )
        
        assert download_url == "https://test.blob.core.windows.net/test.zip"
        
        # Verify upload was called
        mock_file_handler.upload_to_blob.assert_called_once()
        
        # Check ZIP was created
        call_args = mock_file_handler.upload_to_blob.call_args
        zip_path = call_args[0][0]
        assert zip_path.endswith('.zip')
        
        # Verify cleanup (file should not exist)
        assert not os.path.exists(f"/tmp/{job_id}_packaging")
    
    @pytest.mark.asyncio
    async def test_create_package_with_zip_contents(self, packager, mock_file_handler):
        """Test that ZIP file contains expected structure."""
        job_id = "test-job-789"
        results = {"data": "test"}
        original_filename = "document.docx"
        
        # Intercept the ZIP file before it's deleted
        created_zip_path = None
        
        async def capture_zip(zip_path, blob_path):
            nonlocal created_zip_path
            # Copy the ZIP before it's deleted
            import shutil
            created_zip_path = f"/tmp/test_copy_{job_id}.zip"
            shutil.copy2(zip_path, created_zip_path)
            return "https://test.blob.core.windows.net/test.zip"
        
        mock_file_handler.upload_to_blob.side_effect = capture_zip
        
        await packager.create_package(job_id, results, original_filename)
        
        # Verify ZIP contents
        assert created_zip_path is not None
        assert os.path.exists(created_zip_path)
        
        with zipfile.ZipFile(created_zip_path, 'r') as zf:
            namelist = zf.namelist()
            
            # Check standard directories
            assert any('original/' in name for name in namelist)
            assert any('processed/' in name for name in namelist)
            assert any('metadata/' in name for name in namelist)
            assert any('reports/' in name for name in namelist)
            
            # Check summary.json
            assert 'summary.json' in namelist
            
            # Check test file from our implementation
            assert any('processed/test_output.txt' in name for name in namelist)
        
        # Cleanup
        os.remove(created_zip_path)
    
    @pytest.mark.asyncio
    async def test_create_package_error_handling(self, packager, mock_file_handler):
        """Test error handling during package creation."""
        mock_file_handler.upload_to_blob.side_effect = Exception("Upload failed")
        
        with pytest.raises(Exception) as exc_info:
            await packager.create_package(
                "error-job", {}, "file.txt"
            )
        
        assert "Upload failed" in str(exc_info.value)
    
    @pytest.mark.asyncio
    async def test_get_file_listing(self, packager):
        """Test file listing extraction from package stats."""
        package_stats = {
            "files": [
                {"path": "doc.pdf", "type": "pdf", "description": "Original document"},
                {"path": "output.txt", "type": "text", "description": "Processed text"}
            ]
        }
        
        files = packager._get_file_listing(package_stats)
        
        assert len(files) == 2
        assert files[0]["path"] == "doc.pdf"
        assert files[0]["type"] == "pdf"
        assert files[0]["description"] == "Original document"
        assert files[1]["path"] == "output.txt"
    
    @pytest.mark.asyncio
    async def test_cleanup_on_error(self, packager, mock_file_handler):
        """Test that temporary files are cleaned up even on error."""
        job_id = "cleanup-test"
        
        # Make the service implementation raise an error
        async def failing_package(*args):
            raise ValueError("Processing failed")
        
        packager._package_service_results = failing_package
        
        with pytest.raises(ValueError):
            await packager.create_package(job_id, {}, "file.txt")
        
        # Verify temp directory was cleaned up
        assert not os.path.exists(f"/tmp/{job_id}_packaging")
    
    @pytest.mark.asyncio
    async def test_unicode_handling(self, packager):
        """Test handling of unicode characters in files."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Test unicode in JSON
            unicode_data = {
                "text": "Hello 你好 مرحبا",
                "emoji": "🎉🔥💯",
                "special": "café résumé naïve"
            }
            json_path = os.path.join(temp_dir, "unicode.json")
            
            await packager._save_json_file(unicode_data, json_path)
            
            with open(json_path, 'r', encoding='utf-8') as f:
                loaded = json.load(f)
            assert loaded == unicode_data
            
            # Test unicode in text
            unicode_text = "Unicode test: 日本語 한국어 العربية\nEmojis: 😀😎🚀"
            text_path = os.path.join(temp_dir, "unicode.txt")
            
            await packager._save_text_file(unicode_text, text_path)
            
            with open(text_path, 'r', encoding='utf-8') as f:
                loaded_text = f.read()
            assert loaded_text == unicode_text