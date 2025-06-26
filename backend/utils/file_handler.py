#backend/utils/file_handler.py
"""
File handling with Azure Blob Storage integration
==================================================

Provides unified file operations for cognitive services with both local and cloud
storage support, including upload, download, and archive creation capabilities:

## Key Features:
- Azure Blob Storage integration with fallback support
- Automatic file organization by date and job ID
- ZIP archive creation with directory structure
- Temporary file management and cleanup
- MIME type detection and content settings

The file handler manages both temporary local storage and persistent cloud storage,
handling file uploads from the frontend and organizing results for download.

## Performance Optimizations:
- Direct blob streaming for large files
- Efficient ZIP compression with structure
- Automatic cleanup of temporary files
- Connection reuse through client manager
- Smart UUID prefix removal in archives
"""
import os
import tempfile
import uuid
from typing import Optional, Dict, Any, List
from pathlib import Path
from datetime import datetime
import mimetypes

from fastapi import UploadFile
from azure.storage.blob import BlobServiceClient, ContentSettings
from azure.core.exceptions import ResourceNotFoundError

from models.base import FileMetadata, ServiceType
from utils.config import get_config
from utils.logging import get_logger
from utils.exceptions import StorageException


logger = get_logger(__name__)


class FileHandler:
    """Handles file operations with Azure Blob Storage."""
    
    def __init__(self):
        self.config = get_config()
        self.temp_dir = Path(tempfile.gettempdir()) / "cognitive_services"
        self.temp_dir.mkdir(exist_ok=True)
        
        # Initialize blob service client using centralized azure_clients
        try:
            # Import here to avoid circular dependency
            from utils.azure_clients import get_blob_service_client, get_container_client
            
            self.blob_service_client = get_blob_service_client()
            self.container_name = self.config.storage_container
            
            # Ensure container exists
            container_client = get_container_client(self.container_name)
            try:
                container_client.get_container_properties()
                logger.info(f"Connected to blob container: {self.container_name}")
            except ResourceNotFoundError:
                # Create container if it doesn't exist
                container_client.create_container()
                logger.info(f"Created blob container: {self.container_name}")
                
        except Exception as e:
            logger.error(f"Failed to initialize blob storage: {e}")
            self.blob_service_client = None
            self.container_name = None
            logger.warning("Azure Storage not configured - file operations will use local storage only")
    
    async def upload_file(
        self,
        file: UploadFile,
        job_id: str,
        service_type: ServiceType,
        max_size_override: Optional[int] = None
    ) -> FileMetadata:
        """
        Upload a file to Azure Blob Storage.
        
        Args:
            file: Uploaded file
            job_id: Job ID for organizing files
            service_type: Service type
            max_size_override: Override default max file size
            
        Returns:
            FileMetadata object
        """
        if not self.blob_service_client:
            raise StorageException(
                message="Azure Storage is not configured",
                operation="upload"
            )
        
        try:
            # Read file content
            file_content = await file.read()
            file_size = len(file_content)
            
            # Check file size
            max_size = max_size_override or self.config.max_file_size_bytes
            if file_size > max_size:
                raise StorageException(
                    message=f"File too large: {file_size} bytes (max: {max_size})",
                    operation="upload"
                )
            
            # Generate storage path
            filename = file.filename or "unknown"
            storage_path = self._generate_storage_path(job_id, filename)
            
            # Determine MIME type
            mime_type = file.content_type or mimetypes.guess_type(filename)[0] or "application/octet-stream"
            
            # Get blob client
            blob_client = self.blob_service_client.get_blob_client(
                container=self.container_name,
                blob=storage_path
            )
            
            # Uploading to blob storage
            
            # Set content settings
            content_settings = ContentSettings(content_type=mime_type)
            
            # Upload blob with proper content settings
            try:
                # Try with ContentSettings object
                blob_client.upload_blob(
                    file_content,
                    overwrite=True,
                    content_settings=content_settings
                )
            except Exception as e:
                logger.warning(f"Failed with ContentSettings object: {e}, trying alternative method")
                # Fallback - try without content_settings
                try:
                    blob_client.upload_blob(
                        file_content,
                        overwrite=True
                    )
                    # Set content type separately if needed
                    blob_client.set_blob_metadata(
                        metadata={"content_type": mime_type}
                    )
                except Exception as e2:
                    logger.error(f"Both upload methods failed: {e2}")
                    raise
            
            # Create metadata
            metadata = FileMetadata(
                filename=filename,
                size_bytes=file_size,
                mime_type=mime_type,
                storage_path=storage_path
            )
            
            logger.info(f"File uploaded: {filename} -> {storage_path} ({file_size} bytes)")
            return metadata
            
        except Exception as e:
            logger.error(f"Failed to upload file: {e}")
            raise StorageException(
                message=f"Failed to upload file: {str(e)}",
                operation="upload"
            )
    
    async def download_file(
        self,
        storage_path: str,
        local_path: Optional[str] = None
    ) -> str:
        """
        Download a file from Azure Blob Storage.
        
        Args:
            storage_path: Path in blob storage
            local_path: Local path to save file (temp file if None)
            
        Returns:
            Local file path
        """
        if not self.blob_service_client:
            raise StorageException(
                message="Azure Storage is not configured",
                operation="download"
            )
        
        try:
            # Get blob client
            blob_client = self.blob_service_client.get_blob_client(
                container=self.container_name,
                blob=storage_path
            )
            
            # Determine local path
            if local_path is None:
                filename = Path(storage_path).name
                local_path = str(self.temp_dir / f"{uuid.uuid4()}_{filename}")
            
            # Download blob
            with open(local_path, "wb") as download_file:
                download_stream = blob_client.download_blob()
                download_file.write(download_stream.readall())
            
            logger.info(f"File downloaded: {storage_path} -> {local_path}")
            return local_path
            
        except ResourceNotFoundError:
            raise StorageException(
                message=f"File not found: {storage_path}",
                operation="download"
            )
        except Exception as e:
            logger.error(f"Failed to download file: {e}")
            raise StorageException(
                message=f"Failed to download file: {str(e)}",
                operation="download"
            )
    
    async def download_to_path(self, storage_path: str, local_path: str) -> None:
        """
        Download a file from storage to a specific local path.
        
        Args:
            storage_path: Path in blob storage
            local_path: Local path to save the file
        """
        if not self.blob_service_client:
            raise StorageException(
                message="Blob storage not configured",
                operation="download"
            )
        
        try:
            blob_client = self.blob_service_client.get_blob_client(
                container=self.container_name,
                blob=storage_path
            )
            
            # Download directly to the specified path
            with open(local_path, "wb") as f:
                download_stream = blob_client.download_blob()
                f.write(download_stream.readall())
            
            logger.info(f"File downloaded from storage: {storage_path} to {local_path}")
            
        except ResourceNotFoundError:
            raise StorageException(
                message=f"File not found: {storage_path}",
                operation="download"
            )
        except Exception as e:
            logger.error(f"Failed to download file: {e}")
            raise StorageException(
                message=f"Failed to download file: {str(e)}",
                operation="download"
            )
    
    async def delete_file(self, storage_path: str) -> bool:
        """
        Delete a file from storage.
        
        Args:
            storage_path: Path in blob storage
            
        Returns:
            True if file was deleted
        """
        if not self.blob_service_client:
            return False
        
        try:
            blob_client = self.blob_service_client.get_blob_client(
                container=self.container_name,
                blob=storage_path
            )
            blob_client.delete_blob()
            logger.info(f"File deleted: {storage_path}")
            return True
            
        except ResourceNotFoundError:
            logger.warning(f"File not found for deletion: {storage_path}")
            return False
        except Exception as e:
            logger.error(f"Failed to delete file: {e}")
            return False
    
    async def create_temp_file(
        self,
        content: bytes,
        filename: str
    ) -> str:
        """
        Create a temporary local file.
        
        Args:
            content: File content
            filename: Original filename
            
        Returns:
            Path to temporary file
        """
        temp_filename = f"{uuid.uuid4()}_{filename}"
        temp_path = str(self.temp_dir / temp_filename)
        
        with open(temp_path, "wb") as f:
            f.write(content)
        
        # Created temp file
        return temp_path
    
    async def cleanup_temp_files(self, max_age_hours: int = 24) -> int:
        """
        Clean up old temporary files.
        
        Args:
            max_age_hours: Maximum age in hours
            
        Returns:
            Number of files cleaned up
        """
        cleanup_count = 0
        cutoff_time = datetime.now().timestamp() - (max_age_hours * 3600)
        
        try:
            for file_path in self.temp_dir.glob("*"):
                if file_path.is_file():
                    if file_path.stat().st_mtime < cutoff_time:
                        file_path.unlink()
                        cleanup_count += 1
            
            if cleanup_count > 0:
                logger.info(f"Cleaned up {cleanup_count} temporary files")
                
        except Exception as e:
            logger.error(f"Error during temp file cleanup: {e}")
        
        return cleanup_count
    
    async def list_files(self, prefix: str = "") -> List[str]:
        """
        List files in storage with optional prefix filter.
        
        Args:
            prefix: Prefix to filter files
            
        Returns:
            List of blob names
        """
        if not self.blob_service_client:
            return []
        
        try:
            container_client = self.blob_service_client.get_container_client(self.container_name)
            blobs = container_client.list_blobs(name_starts_with=prefix)
            return [blob.name for blob in blobs]
        except Exception as e:
            logger.error(f"Failed to list files: {e}")
            return []
    
    async def file_exists(self, storage_path: str) -> bool:
        """Check if a file exists in storage."""
        if not self.blob_service_client:
            return False
        
        try:
            blob_client = self.blob_service_client.get_blob_client(
                container=self.container_name,
                blob=storage_path
            )
            return blob_client.exists()
        except Exception:
            return False
    
    def _generate_storage_path(self, job_id: str, filename: str) -> str:
        """Generate storage path for a file."""
        # Organize by date and job ID
        date_path = datetime.utcnow().strftime("%Y/%m/%d")
        return f"{date_path}/{job_id}/{filename}"
    
    async def zip_files(
        self,
        file_paths: List[str],
        zip_filename: str,
        job_id: str
    ) -> str:
        """
        Create a ZIP archive of multiple files.
        
        Args:
            file_paths: List of file paths to include
            zip_filename: Name for the ZIP file
            job_id: Job ID for organizing
            
        Returns:
            Path to ZIP file in storage
        """
        import zipfile
        
        # Create temp ZIP file
        temp_zip_path = str(self.temp_dir / f"{uuid.uuid4()}_{zip_filename}")
        
        try:
            with zipfile.ZipFile(temp_zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                for file_path in file_paths:
                    if os.path.exists(file_path):
                        filename = Path(file_path).name
                        
                        # Remove UUID prefix if present (format: uuid_filename)
                        if '_' in filename and len(filename.split('_')[0]) == 36:
                            # First part looks like a UUID (36 chars), remove it
                            filename = '_'.join(filename.split('_')[1:])
                        
                        # Determine directory structure based on file type
                        if filename.endswith('.csv'):
                            arcname = f"csv/{filename}"
                        elif filename.endswith('_tables.xlsx'):
                            arcname = filename  # Excel file goes in root
                        elif filename.endswith('.md'):
                            # Check if it's a page file
                            if '_page' in filename and filename.split('_page')[1].startswith(tuple(str(i) for i in range(10))):
                                arcname = f"md/md_pages/{filename}"
                            else:
                                arcname = f"md/{filename}"
                        elif filename.endswith('_confidence_dashboard.png'):
                            arcname = filename  # Dashboard goes in root
                        elif filename == 'analysis_summary.json':
                            arcname = filename  # Summary goes in root
                        else:
                            arcname = filename  # Default to root
                        
                        zipf.write(file_path, arcname)
            
            # Upload ZIP to storage
            storage_path = self._generate_storage_path(job_id, zip_filename)
            
            # Create a mock UploadFile object for the zip
            class ZipUploadFile:
                def __init__(self, path, name):
                    self.filename = name
                    self.content_type = "application/zip"
                    self._path = path
                
                async def read(self):
                    with open(self._path, "rb") as f:
                        return f.read()
            
            zip_upload = ZipUploadFile(temp_zip_path, zip_filename)
            metadata = await self.upload_file(zip_upload, job_id, ServiceType.DOCUMENT_INTELLIGENCE)
            
            logger.info(f"Created ZIP archive: {zip_filename}")
            return metadata.storage_path
            
        finally:
            # Clean up temp ZIP file
            if os.path.exists(temp_zip_path):
                os.remove(temp_zip_path)
    
    async def zip_files_with_structure(
        self,
        files_dict: Dict[str, str],
        zip_filename: str,
        job_id: str
    ) -> str:
        """
        Create a ZIP archive with directory structure.
        
        Args:
            files_dict: Dictionary mapping archive paths to local file paths
            zip_filename: Name for the ZIP file
            job_id: Job ID for organizing
            
        Returns:
            Path to ZIP file in storage
        """
        import zipfile
        
        # Create temp ZIP file
        temp_zip_path = str(self.temp_dir / f"{uuid.uuid4()}_{zip_filename}")
        
        try:
            with zipfile.ZipFile(temp_zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                for arc_path, file_path in files_dict.items():
                    if os.path.exists(file_path):
                        zipf.write(file_path, arc_path)
            
            # Upload ZIP to storage
            storage_path = self._generate_storage_path(job_id, zip_filename)
            
            # Create a mock UploadFile object for the zip
            class ZipUploadFile:
                def __init__(self, path, name):
                    self.filename = name
                    self.content_type = "application/zip"
                    self._path = path
                
                async def read(self):
                    with open(self._path, "rb") as f:
                        return f.read()
            
            zip_upload = ZipUploadFile(temp_zip_path, zip_filename)
            metadata = await self.upload_file(zip_upload, job_id, ServiceType.DOCUMENT_INTELLIGENCE)
            
            logger.info(f"Created ZIP archive with structure: {zip_filename}")
            return metadata.storage_path
            
        finally:
            # Clean up temp ZIP file
            if os.path.exists(temp_zip_path):
                os.remove(temp_zip_path)


# Global file handler instance
_file_handler: Optional[FileHandler] = None


def get_file_handler() -> FileHandler:
    """Get global file handler instance."""
    global _file_handler
    if _file_handler is None:
        _file_handler = FileHandler()
    return _file_handler


# Convenience functions for backward compatibility
async def upload_file(
    file: UploadFile,
    job_id: str,
    service_type: ServiceType,
    max_size_override: Optional[int] = None
) -> FileMetadata:
    """Upload a file."""
    return await get_file_handler().upload_file(file, job_id, service_type, max_size_override)


async def download_file(
    storage_path: str,
    local_path: Optional[str] = None
) -> str:
    """Download a file."""
    return await get_file_handler().download_file(storage_path, local_path)


async def delete_file(storage_path: str) -> bool:
    """Delete a file."""
    return await get_file_handler().delete_file(storage_path)


async def create_temp_file(
    content: bytes,
    filename: str
) -> str:
    """Create a temporary file."""
    return await get_file_handler().create_temp_file(content, filename)


async def zip_files(
    file_paths: List[str],
    zip_filename: str,
    job_id: str
) -> str:
    """Create a ZIP archive."""
    return await get_file_handler().zip_files(file_paths, zip_filename, job_id)