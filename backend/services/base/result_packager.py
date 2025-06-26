# backend/services/base/result_packager.py
"""
Unified Result Packager for Cognitive Services
==============================================

Provides a standardized approach to packaging results across all cognitive services,
ensuring consistent ZIP structure, metadata format, and storage integration:

## Key Features:
----------------
- Standardized ZIP directory structure
- Common metadata format across services
- Automatic file organization
- Azure Blob Storage integration
- Progress tracking support
- Cleanup of temporary files

## ZIP Structure:
-----------------
{job_id}_{service}_results.zip
├── original/              # Original input files
├── processed/             # Processed output files
├── metadata/              # Metadata and analysis files
│   ├── summary.json       # Standardized summary
│   └── {service}_specific.json  # Service-specific metadata
└── reports/              # Human-readable reports (optional)

"""

import os
import json
import tempfile
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime
from abc import ABC, abstractmethod

from utils.file_handler import get_file_handler
from utils.logging import get_logger
from models.base import ServiceType

logger = get_logger(__name__)


class ResultPackager(ABC):
    """Base class for standardized result packaging across services."""
    
    def __init__(self, service_type: ServiceType):
        """
        Initialize the result packager.
        
        Args:
            service_type: The type of cognitive service
        """
        self.service_type = service_type
        self.file_handler = get_file_handler()
    
    async def create_package(
        self,
        job_id: str,
        processing_results: Dict[str, Any],
        original_file_path: Optional[str] = None,
        original_filename: Optional[str] = None,
        processing_time_seconds: float = 0.0,
        cost_estimate: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Create a standardized results package.
        
        Args:
            job_id: Job identifier
            processing_results: Service-specific processing results
            original_file_path: Path to original input file
            original_filename: Name of original file
            processing_time_seconds: Time taken to process
            cost_estimate: Optional cost estimation
            
        Returns:
            Path to created ZIP file in storage
        """
        temp_dir = None
        try:
            # Create temporary directory structure
            temp_dir = Path(tempfile.mkdtemp(prefix=f"{job_id}_package_"))
            
            # Create standard directories
            original_dir = temp_dir / "original"
            processed_dir = temp_dir / "processed"
            metadata_dir = temp_dir / "metadata"
            reports_dir = temp_dir / "reports"
            
            for dir_path in [original_dir, processed_dir, metadata_dir, reports_dir]:
                dir_path.mkdir(exist_ok=True)
            
            # Copy original file if provided
            if original_file_path and os.path.exists(original_file_path):
                original_filename = original_filename or Path(original_file_path).name
                target_path = original_dir / original_filename
                import shutil
                shutil.copy2(original_file_path, target_path)
            
            # Generate service-specific files
            await self._generate_service_files(
                processing_results,
                processed_dir,
                metadata_dir,
                reports_dir
            )
            
            # Create standardized summary metadata
            summary_metadata = self._create_summary_metadata(
                job_id=job_id,
                original_filename=original_filename,
                original_file_size=os.path.getsize(original_file_path) if original_file_path and os.path.exists(original_file_path) else 0,
                processing_results=processing_results,
                processing_time_seconds=processing_time_seconds,
                cost_estimate=cost_estimate
            )
            
            # Write summary metadata
            summary_path = metadata_dir / "summary.json"
            with open(summary_path, 'w', encoding='utf-8') as f:
                json.dump(summary_metadata, f, indent=2, ensure_ascii=False)
            
            # Create service-specific metadata
            service_metadata = await self._create_service_metadata(processing_results)
            if service_metadata:
                service_metadata_path = metadata_dir / f"{self.service_type.value}_metadata.json"
                with open(service_metadata_path, 'w', encoding='utf-8') as f:
                    json.dump(service_metadata, f, indent=2, ensure_ascii=False)
            
            # Collect all files for ZIP
            all_files = []
            for root, _, files in os.walk(temp_dir):
                for file in files:
                    file_path = Path(root) / file
                    # Calculate relative path from temp_dir
                    rel_path = file_path.relative_to(temp_dir)
                    all_files.append((str(file_path), str(rel_path)))
            
            # Create ZIP with structure
            zip_filename = f"{job_id}_{self.service_type.value}_results.zip"
            files_dict = {arc_path: file_path for file_path, arc_path in all_files}
            
            zip_path = await self.file_handler.zip_files_with_structure(
                files_dict,
                zip_filename,
                job_id
            )
            
            logger.info(
                f"Created {self.service_type.value} results package: {zip_filename} "
                f"with {len(all_files)} files"
            )
            
            return zip_path
            
        except Exception as e:
            logger.error(f"Error creating results package: {e}")
            raise
        finally:
            # Cleanup temporary directory
            if temp_dir and temp_dir.exists():
                import shutil
                try:
                    shutil.rmtree(temp_dir)
                except Exception as e:
                    logger.debug(f"Could not remove temp directory {temp_dir}: {e}")
    
    def _create_summary_metadata(
        self,
        job_id: str,
        original_filename: Optional[str],
        original_file_size: int,
        processing_results: Dict[str, Any],
        processing_time_seconds: float,
        cost_estimate: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Create standardized summary metadata."""
        # Count generated files
        files_generated = self._count_generated_files(processing_results)
        
        # Get primary result path
        primary_result = self._get_primary_result_path(processing_results)
        
        # Get service-specific statistics
        statistics = self._extract_statistics(processing_results)
        
        summary = {
            "job_id": job_id,
            "service": self.service_type.value,
            "processing_time_seconds": processing_time_seconds,
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "input": {
                "filename": original_filename or "unknown",
                "size_bytes": original_file_size,
                "mime_type": self._get_mime_type(original_filename) if original_filename else "unknown"
            },
            "output": {
                "files_generated": files_generated,
                "primary_result": primary_result
            },
            "statistics": statistics
        }
        
        if cost_estimate:
            summary["cost_estimate"] = cost_estimate
        
        return summary
    
    def _get_mime_type(self, filename: str) -> str:
        """Get MIME type from filename."""
        import mimetypes
        mime_type = mimetypes.guess_type(filename)[0]
        return mime_type or "application/octet-stream"
    
    @abstractmethod
    async def _generate_service_files(
        self,
        processing_results: Dict[str, Any],
        processed_dir: Path,
        metadata_dir: Path,
        reports_dir: Path
    ) -> None:
        """
        Generate service-specific files in the appropriate directories.
        
        Must be implemented by each service.
        """
        pass
    
    @abstractmethod
    async def _create_service_metadata(
        self,
        processing_results: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """
        Create service-specific metadata.
        
        Must be implemented by each service.
        """
        pass
    
    @abstractmethod
    def _count_generated_files(self, processing_results: Dict[str, Any]) -> int:
        """Count the number of files generated by the service."""
        pass
    
    @abstractmethod
    def _get_primary_result_path(self, processing_results: Dict[str, Any]) -> str:
        """Get the path to the primary result file."""
        pass
    
    @abstractmethod
    def _extract_statistics(self, processing_results: Dict[str, Any]) -> Dict[str, Any]:
        """Extract service-specific statistics."""
        pass