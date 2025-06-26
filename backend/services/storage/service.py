# backend/services/storage/service.py
"""
Storage Service
===============

Service wrapper for Azure Blob Storage operations using account key authentication.
"""

import os
import io
import logging
from typing import List, Dict, Any, Tuple, Optional
from datetime import datetime, timedelta, timezone
from azure.storage.blob import BlobServiceClient, ContentSettings
import asyncio
from concurrent.futures import ThreadPoolExecutor

logger = logging.getLogger(__name__)


class StorageService:
    """Service for Azure Blob Storage operations."""
    
    def __init__(self):
        """Initialize the service with Azure credentials."""
        # Get credentials from environment
        self.account_name = os.getenv("AZURE_STORAGE_ACCOUNT_NAME")
        self.account_key = os.getenv("AZURE_STORAGE_ACCOUNT_KEY")
        self.container_name = os.getenv("AZURE_STORAGE_CONTAINER", "cognitive-services")
        
        # Validate required configuration
        if not self.account_name:
            raise ValueError("AZURE_STORAGE_ACCOUNT_NAME not configured")
        if not self.account_key:
            raise ValueError("AZURE_STORAGE_ACCOUNT_KEY not configured")
        
        # Create blob service client
        try:
            account_url = f"https://{self.account_name}.blob.core.windows.net"
            self.blob_service_client = BlobServiceClient(
                account_url=account_url, 
                credential=self.account_key
            )
            logger.info(f"Connected to Azure Storage account: {self.account_name}")
        except Exception as e:
            logger.error(f"Failed to create BlobServiceClient: {str(e)}")
            raise ValueError(f"Invalid Azure Storage credentials: {str(e)}")
        
        # Thread pool for async operations
        self._executor = ThreadPoolExecutor(max_workers=10)
        
        # Ensure container exists
        self._ensure_container_exists()
    
    def _ensure_container_exists(self):
        """Ensure the storage container exists."""
        try:
            container_client = self.blob_service_client.get_container_client(self.container_name)
            try:
                # Try to get container properties to check if it exists
                container_client.get_container_properties()
                logger.info(f"Container exists: {self.container_name}")
            except Exception as e:
                if "ContainerNotFound" in str(e):
                    container_client.create_container()
                    logger.info(f"Created container: {self.container_name}")
                else:
                    raise
        except Exception as e:
            logger.error(f"Error checking/creating container: {str(e)}")
            raise
    
    def _run_sync(self, func, *args, **kwargs):
        """Run a synchronous function in the thread pool."""
        loop = asyncio.get_event_loop()
        # Create a partial function with kwargs if provided
        if kwargs:
            from functools import partial
            func = partial(func, *args, **kwargs)
            return loop.run_in_executor(self._executor, func)
        else:
            return loop.run_in_executor(self._executor, func, *args)
    
    async def upload_file(
        self,
        file_name: str,
        file_content: bytes,
        folder: str = "uploads",
        content_type: str = "application/octet-stream"
    ) -> Dict[str, Any]:
        """
        Upload a file to Azure Blob Storage.
        
        Args:
            file_name: Name of the file
            file_content: File content as bytes
            folder: Folder path in storage
            content_type: MIME type of the file
        
        Returns:
            File metadata and URL
        """
        try:
            # Generate blob name with folder structure
            timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
            blob_name = f"{folder}/{timestamp}_{file_name}"
            
            # Get blob client
            blob_client = self.blob_service_client.get_blob_client(
                container=self.container_name,
                blob=blob_name
            )
            
            # Set content settings
            content_settings = ContentSettings(content_type=content_type)
            
            # Upload blob asynchronously
            await self._run_sync(
                blob_client.upload_blob,
                file_content,
                content_settings=content_settings,
                overwrite=True
            )
            
            # Generate URL
            url = blob_client.url
            
            return {
                'file_name': file_name,
                'file_path': blob_name,
                'size': len(file_content),
                'content_type': content_type,
                'url': url,
                'created_at': datetime.now(timezone.utc)
            }
            
        except Exception as e:
            logger.error(f"Upload error: {str(e)}")
            raise
    
    async def download_file(self, file_path: str) -> Tuple[io.BytesIO, str, str]:
        """
        Download a file from storage.
        
        Args:
            file_path: Path to file in storage
        
        Returns:
            Tuple of (file stream, content type, file name)
        """
        try:
            blob_client = self.blob_service_client.get_blob_client(
                container=self.container_name,
                blob=file_path
            )
            
            # Check if blob exists
            exists = await self._run_sync(blob_client.exists)
            if not exists:
                raise FileNotFoundError(f"File not found: {file_path}")
            
            # Download blob
            blob_data = await self._run_sync(blob_client.download_blob)
            content = await self._run_sync(blob_data.readall)
            
            # Get properties
            properties = await self._run_sync(blob_client.get_blob_properties)
            content_type = properties.content_settings.content_type if properties.content_settings else "application/octet-stream"
            
            # Extract filename from path
            file_name = os.path.basename(file_path)
            
            # Create BytesIO stream
            stream = io.BytesIO(content)
            stream.seek(0)
            
            return stream, content_type, file_name
            
        except Exception as e:
            logger.error(f"Download error: {str(e)}")
            raise
    
    async def list_files(
        self,
        folder: str = "",
        prefix: str = "",
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """
        List files in storage.
        
        Args:
            folder: Folder path to list
            prefix: File name prefix filter
            limit: Maximum number of files
        
        Returns:
            List of file metadata
        """
        try:
            container_client = self.blob_service_client.get_container_client(self.container_name)
            
            # Build prefix
            full_prefix = folder
            if prefix:
                full_prefix = f"{folder}/{prefix}" if folder else prefix
            
            # List blobs synchronously in thread pool
            def _list_blobs():
                files = []
                count = 0
                
                # Use list_blobs without max_results parameter
                blob_iter = container_client.list_blobs(name_starts_with=full_prefix if full_prefix else None)
                
                for blob in blob_iter:
                    if count >= limit:
                        break
                    
                    # Build URL
                    blob_url = f"{self.blob_service_client.url}{self.container_name}/{blob.name}"
                    
                    files.append({
                        'name': os.path.basename(blob.name),
                        'path': blob.name,
                        'size': blob.size,
                        'content_type': blob.content_settings.content_type if blob.content_settings else 'application/octet-stream',
                        'created_at': blob.creation_time.replace(tzinfo=timezone.utc) if blob.creation_time else None,
                        'modified_at': blob.last_modified.replace(tzinfo=timezone.utc) if blob.last_modified else None,
                        'url': blob_url
                    })
                    count += 1
                
                return files
            
            return await self._run_sync(_list_blobs)
            
        except Exception as e:
            logger.error(f"List files error: {str(e)}")
            raise
    
    async def delete_file(self, file_path: str) -> bool:
        """
        Delete a file from storage.
        
        Args:
            file_path: Path to file in storage
        
        Returns:
            Success status
        """
        try:
            blob_client = self.blob_service_client.get_blob_client(
                container=self.container_name,
                blob=file_path
            )
            
            # Check if blob exists
            exists = await self._run_sync(blob_client.exists)
            if not exists:
                raise FileNotFoundError(f"File not found: {file_path}")
            
            # Delete blob
            await self._run_sync(blob_client.delete_blob)
            
            return True
            
        except Exception as e:
            logger.error(f"Delete error: {str(e)}")
            raise
    
    async def cleanup_old_files(self, days_old: int = 7) -> int:
        """
        Clean up files older than specified days.
        
        Args:
            days_old: Delete files older than this many days
        
        Returns:
            Number of files deleted
        """
        try:
            container_client = self.blob_service_client.get_container_client(self.container_name)
            cutoff_date = datetime.now(timezone.utc) - timedelta(days=days_old)
            
            def _cleanup():
                deleted_count = 0
                blob_iter = container_client.list_blobs()
                
                for blob in blob_iter:
                    # Ensure timezone-aware comparison
                    blob_modified = blob.last_modified
                    if blob_modified.tzinfo is None:
                        blob_modified = blob_modified.replace(tzinfo=timezone.utc)
                    
                    if blob_modified < cutoff_date:
                        try:
                            blob_client = container_client.get_blob_client(blob.name)
                            blob_client.delete_blob()
                            deleted_count += 1
                            logger.info(f"Deleted old file: {blob.name}")
                        except Exception as e:
                            logger.error(f"Failed to delete {blob.name}: {str(e)}")
                
                return deleted_count
            
            return await self._run_sync(_cleanup)
            
        except Exception as e:
            logger.error(f"Cleanup error: {str(e)}")
            raise
    
    async def upload_file_from_path(
        self,
        file_path: str,
        blob_name: str,
        content_type: str = "application/octet-stream"
    ) -> str:
        """
        Upload a file from a local path to Azure Blob Storage.
        
        Args:
            file_path: Local path to the file
            blob_name: Name/path for the blob in storage
            content_type: MIME type of the file
        
        Returns:
            Blob path in storage
        """
        try:
            # Read file content
            with open(file_path, 'rb') as f:
                file_content = f.read()
            
            # Get blob client directly with the specified blob name
            blob_client = self.blob_service_client.get_blob_client(
                container=self.container_name,
                blob=blob_name
            )
            
            # Set content settings
            content_settings = ContentSettings(content_type=content_type)
            
            # Upload blob asynchronously
            await self._run_sync(
                blob_client.upload_blob,
                file_content,
                content_settings=content_settings,
                overwrite=True
            )
            
            logger.info(f"Uploaded file from {file_path} to {blob_name}")
            
            # Return the blob name (path in storage)
            return blob_name
            
        except Exception as e:
            logger.error(f"Upload from path error: {str(e)}")
            raise
    
    async def download_to_path(
        self,
        blob_name: str,
        local_path: str
    ) -> str:
        """
        Download a file from Azure Blob Storage to a local path.
        
        Args:
            blob_name: Name/path of the blob in storage
            local_path: Local path where the file will be saved
        
        Returns:
            Local path where the file was saved
        """
        try:
            blob_client = self.blob_service_client.get_blob_client(
                container=self.container_name,
                blob=blob_name
            )
            
            # Check if blob exists
            exists = await self._run_sync(blob_client.exists)
            if not exists:
                raise FileNotFoundError(f"Blob not found: {blob_name}")
            
            # Download blob
            blob_data = await self._run_sync(blob_client.download_blob)
            content = await self._run_sync(blob_data.readall)
            
            # Ensure directory exists
            os.makedirs(os.path.dirname(local_path), exist_ok=True)
            
            # Write to local file
            with open(local_path, 'wb') as f:
                f.write(content)
            
            logger.info(f"Downloaded blob {blob_name} to {local_path}")
            
            return local_path
            
        except Exception as e:
            logger.error(f"Download to path error: {str(e)}")
            raise
    
    
    def close(self):
        """Clean up resources."""
        if hasattr(self, '_executor'):
            self._executor.shutdown(wait=True)


# Singleton instance
_storage_service = None


def get_storage_service() -> StorageService:
    """Get the storage service instance."""
    global _storage_service
    if _storage_service is None:
        _storage_service = StorageService()
    return _storage_service