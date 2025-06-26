"""
Result packaging utilities for all cognitive services.

This module provides a base class and implementations for creating standardized
result packages (ZIP files) across all services.
"""
import os
import json
import shutil
from abc import ABC, abstractmethod
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional, List
import logging

from utils.file_handler import FileHandler
from utils.logging import get_logger

logger = get_logger(__name__)


class ResultPackager(ABC):
    """
    Base class for all service result packagers.
    
    Provides standardized structure and common functionality for creating
    result packages across all cognitive services.
    """
    
    def __init__(self, file_handler: FileHandler):
        """
        Initialize the ResultPackager.
        
        Args:
            file_handler: FileHandler instance for file operations
        """
        self.file_handler = file_handler
        self.logger = get_logger(f"{__name__}.{self.__class__.__name__}")
    
    @property
    @abstractmethod
    def service_name(self) -> str:
        """Get the service name for this packager."""
        pass
    
    @abstractmethod
    async def _package_service_results(
        self, 
        temp_dir: str,
        results: Dict[str, Any],
        original_filename: str,
        metadata: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Package service-specific results.
        
        Args:
            temp_dir: Temporary directory for packaging
            results: Service processing results
            original_filename: Original input filename
            metadata: Additional metadata
            
        Returns:
            Dictionary with packaging statistics
        """
        pass
    
    async def create_package(
        self, 
        job_id: str, 
        results: Dict[str, Any], 
        original_filename: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Create a standardized ZIP package and upload to blob storage.
        
        Args:
            job_id: Unique job identifier
            results: Processing results from service
            original_filename: Original input filename
            metadata: Additional metadata to include
            
        Returns:
            Download URL for the created package
        """
        temp_dir = None
        zip_path = None
        
        try:
            # Create temporary directory
            temp_dir = f"/tmp/{job_id}_packaging"
            os.makedirs(temp_dir, exist_ok=True)
            
            # Create standard directory structure
            self._create_standard_structure(temp_dir)
            
            # Package service-specific results
            package_stats = await self._package_service_results(
                temp_dir, results, original_filename, metadata or {}
            )
            
            # Create summary JSON
            summary = self._create_summary_json(
                job_id, original_filename, package_stats, metadata or {}
            )
            summary_path = os.path.join(temp_dir, "summary.json")
            with open(summary_path, 'w', encoding='utf-8') as f:
                json.dump(summary, f, indent=2, ensure_ascii=False)
            
            # Create ZIP file
            zip_filename = f"{job_id}_{self.service_name}_results"
            zip_path = f"/tmp/{zip_filename}"
            shutil.make_archive(zip_path, 'zip', temp_dir)
            zip_path += '.zip'
            
            # Upload to blob storage
            blob_path = f"results/{job_id}/{zip_filename}.zip"
            download_url = await self.file_handler.upload_to_blob(
                zip_path, blob_path
            )
            
            self.logger.info(
                f"Created result package for job {job_id}",
                extra={
                    "job_id": job_id,
                    "service": self.service_name,
                    "package_size": os.path.getsize(zip_path),
                    "files_count": package_stats.get("files_count", 0)
                }
            )
            
            return download_url
            
        except Exception as e:
            self.logger.error(
                f"Failed to create result package for job {job_id}: {str(e)}",
                extra={"job_id": job_id, "service": self.service_name}
            )
            raise
        finally:
            # Cleanup temporary files
            if temp_dir and os.path.exists(temp_dir):
                try:
                    shutil.rmtree(temp_dir)
                except Exception as e:
                    self.logger.warning(f"Failed to cleanup temp dir: {str(e)}")
            
            if zip_path and os.path.exists(zip_path):
                try:
                    os.remove(zip_path)
                except Exception as e:
                    self.logger.warning(f"Failed to cleanup zip file: {str(e)}")
    
    def _create_standard_structure(self, temp_dir: str) -> None:
        """
        Create standard directory structure for all services.
        
        Args:
            temp_dir: Root temporary directory
        """
        directories = ["original", "processed", "metadata", "reports"]
        for directory in directories:
            os.makedirs(os.path.join(temp_dir, directory), exist_ok=True)
    
    def _create_summary_json(
        self, 
        job_id: str,
        original_filename: str,
        package_stats: Dict[str, Any],
        metadata: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Create standardized summary.json file.
        
        Args:
            job_id: Job identifier
            original_filename: Original input filename
            package_stats: Statistics from packaging
            metadata: Additional metadata
            
        Returns:
            Summary dictionary
        """
        return {
            "job_id": job_id,
            "service": self.service_name,
            "original_filename": original_filename,
            "processed_at": datetime.utcnow().isoformat(),
            "package_version": "1.0",
            "statistics": package_stats,
            "metadata": metadata,
            "files": self._get_file_listing(package_stats)
        }
    
    def _get_file_listing(self, package_stats: Dict[str, Any]) -> List[Dict[str, str]]:
        """
        Get listing of files in the package.
        
        Args:
            package_stats: Statistics including file information
            
        Returns:
            List of file entries
        """
        files = []
        if "files" in package_stats:
            for file_info in package_stats["files"]:
                files.append({
                    "path": file_info.get("path", ""),
                    "type": file_info.get("type", ""),
                    "description": file_info.get("description", "")
                })
        return files
    
    async def _save_json_file(
        self, 
        data: Dict[str, Any], 
        file_path: str,
        description: str = "JSON data"
    ) -> Dict[str, str]:
        """
        Save dictionary as JSON file.
        
        Args:
            data: Data to save
            file_path: Full path to save file
            description: Description of the file
            
        Returns:
            File info dictionary
        """
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        return {
            "path": Path(file_path).name,
            "type": "json",
            "description": description,
            "size": os.path.getsize(file_path)
        }
    
    async def _save_text_file(
        self, 
        content: str, 
        file_path: str,
        description: str = "Text file"
    ) -> Dict[str, str]:
        """
        Save text content to file.
        
        Args:
            content: Text content to save
            file_path: Full path to save file
            description: Description of the file
            
        Returns:
            File info dictionary
        """
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        return {
            "path": Path(file_path).name,
            "type": "text",
            "description": description,
            "size": os.path.getsize(file_path)
        }
    
    async def _copy_file(
        self, 
        source_path: str, 
        dest_path: str,
        description: str = "File"
    ) -> Dict[str, str]:
        """
        Copy file to package directory.
        
        Args:
            source_path: Source file path
            dest_path: Destination file path
            description: Description of the file
            
        Returns:
            File info dictionary
        """
        shutil.copy2(source_path, dest_path)
        
        return {
            "path": Path(dest_path).name,
            "type": Path(dest_path).suffix.lstrip('.'),
            "description": description,
            "size": os.path.getsize(dest_path)
        }