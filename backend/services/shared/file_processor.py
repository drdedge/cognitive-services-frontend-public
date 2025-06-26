# backend/services/shared/file_processor.py
"""
File Processor
==============

Unified file processing operations for all services. Wraps existing FileHandler
and StorageService to provide a simple, consistent interface for:
- File uploads to blob storage
- File downloads from blob storage
- Temporary file management
- ZIP package creation
"""

import os
import tempfile
import shutil
from typing import Optional, List, Dict, Any
from pathlib import Path

from fastapi import UploadFile
from utils.file_handler import get_file_handler
from services.storage import get_storage_service
from utils.logging import get_logger
from models.base import ServiceType

logger = get_logger(__name__)


class FileProcessor:
    """
    Simplified file operations for all services.
    
    This class provides a clean interface to common file operations,
    hiding the complexity of blob storage and temp file management.
    """
    
    def __init__(self):
        """Initialize with existing file handler and storage service."""
        self.file_handler = get_file_handler()
        self.storage_service = get_storage_service()
    
    async def save_upload_file(
        self,
        file: UploadFile,
        job_id: str,
        service_type: ServiceType
    ) -> Dict[str, str]:
        """
        Save an uploaded file to blob storage.
        
        Args:
            file: FastAPI UploadFile object
            job_id: Job identifier
            service_type: Type of service (for organizing files)
            
        Returns:
            Dictionary with local_path and blob_path
        """
        # Create a temporary file
        temp_dir = tempfile.mkdtemp()
        temp_path = os.path.join(temp_dir, file.filename)
        
        try:
            # Save uploaded file locally
            content = await file.read()
            with open(temp_path, 'wb') as f:
                f.write(content)
            
            # Upload to blob storage
            blob_path = f"{service_type.value}/{job_id}/input/{file.filename}"
            await self.storage_service.upload_file_from_path(temp_path, blob_path)
            
            logger.info(f"Uploaded file {file.filename} to {blob_path}")
            
            return {
                'local_path': temp_path,
                'blob_path': blob_path,
                'filename': file.filename,
                'size': len(content)
            }
            
        except Exception as e:
            # Cleanup on error
            if os.path.exists(temp_dir):
                shutil.rmtree(temp_dir)
            raise Exception(f"Failed to save upload file: {str(e)}")
    
    async def download_from_blob(
        self,
        blob_path: str,
        local_filename: Optional[str] = None
    ) -> str:
        """
        Download a file from blob storage to a temporary location.
        
        Args:
            blob_path: Path in blob storage
            local_filename: Optional local filename (uses blob name if not provided)
            
        Returns:
            Path to downloaded file
        """
        # Create temp file
        if local_filename:
            temp_path = os.path.join(tempfile.mkdtemp(), local_filename)
        else:
            temp_path = os.path.join(tempfile.mkdtemp(), os.path.basename(blob_path))
        
        # Download from blob
        await self.storage_service.download_to_path(blob_path, temp_path)
        
        logger.info(f"Downloaded {blob_path} to {temp_path}")
        return temp_path
    
    async def create_results_zip(
        self,
        job_id: str,
        files: List[str],
        service_type: ServiceType,
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Create a ZIP file with results and upload to blob storage.
        
        Args:
            job_id: Job identifier
            files: List of file paths to include
            service_type: Type of service
            metadata: Optional metadata to include
            
        Returns:
            Blob path of uploaded ZIP file
        """
        # Create ZIP using existing file_handler
        zip_filename = f"{job_id}_results.zip"
        zip_path = await self.file_handler.zip_files(files, zip_filename, job_id)
        
        # Upload to blob storage
        blob_path = f"{service_type.value}/{job_id}/results/{zip_filename}"
        await self.storage_service.upload_file_from_path(zip_path, blob_path)
        
        # Cleanup local ZIP
        if os.path.exists(zip_path):
            os.remove(zip_path)
        
        logger.info(f"Created and uploaded results ZIP to {blob_path}")
        return blob_path
    
    async def cleanup_job_files(self, job_id: str, service_type: ServiceType) -> int:
        """
        Clean up all files associated with a job.
        
        Args:
            job_id: Job identifier
            service_type: Type of service
            
        Returns:
            Number of files cleaned up
        """
        try:
            # List and delete all blobs for this job
            prefix = f"{service_type.value}/{job_id}/"
            deleted_count = 0
            
            blobs = await self.storage_service.list_blobs(prefix)
            for blob in blobs:
                await self.storage_service.delete_blob(blob['name'])
                deleted_count += 1
            
            logger.info(f"Cleaned up {deleted_count} files for job {job_id}")
            return deleted_count
            
        except Exception as e:
            logger.warning(f"Error cleaning up job {job_id}: {e}")
            return 0
    
    def cleanup_temp_file(self, file_path: str) -> None:
        """
        Clean up a temporary file and its directory if empty.
        
        Args:
            file_path: Path to temporary file
        """
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
                
                # Try to remove parent directory if empty
                parent_dir = os.path.dirname(file_path)
                if os.path.exists(parent_dir) and not os.listdir(parent_dir):
                    os.rmdir(parent_dir)
                    
        except Exception as e:
            logger.warning(f"Error cleaning up temp file {file_path}: {e}")
    
    async def get_file_size(self, blob_path: str) -> int:
        """
        Get the size of a file in blob storage.
        
        Args:
            blob_path: Path in blob storage
            
        Returns:
            File size in bytes
        """
        try:
            props = await self.storage_service.get_blob_properties(blob_path)
            return props.get('size', 0)
        except Exception:
            return 0
    
    async def file_exists(self, blob_path: str) -> bool:
        """
        Check if a file exists in blob storage.
        
        Args:
            blob_path: Path in blob storage
            
        Returns:
            True if file exists
        """
        try:
            await self.storage_service.get_blob_properties(blob_path)
            return True
        except Exception:
            return False