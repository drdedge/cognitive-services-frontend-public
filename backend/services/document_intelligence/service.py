# backend/services/document_intelligence/service.py
"""
Document Intelligence service with Azure Form Recognizer – Core implementation
==============================================================================

This module provides the main service class for document analysis operations using
Azure's Document Intelligence API. It handles the complete processing pipeline from
document submission through result packaging:

## Key Features:
-----------------
- Asynchronous document analysis with progress tracking
- Multi-format support (PDF, DOCX, images)
- Table extraction with CSV and Excel output
- Text extraction with markdown formatting
- Confidence scoring and dashboard generation
- Results packaging in organized ZIP files

## Performance Optimizations:
-----------------------------
- Asynchronous polling with configurable intervals
- Progress callbacks for real-time updates
- Efficient file handling with temporary storage
- Connection pooling for Azure clients
- Memory-efficient streaming for large documents

The service uses the prebuilt-layout model for comprehensive document analysis,
providing consistent and accurate extraction across diverse document types.
"""
import os
import json
import asyncio
from pathlib import Path
from typing import Dict, Any, Optional, Callable, Tuple
from datetime import datetime

from azure.ai.documentintelligence import DocumentIntelligenceClient
from azure.ai.documentintelligence.models import AnalyzeDocumentRequest, DocumentContentFormat

from utils.azure_clients import get_document_intelligence_client
from utils.file_handler import get_file_handler
from utils.job_manager import get_job_manager
from utils.config import get_config
from utils.logging import get_logger, PerformanceTimer, log_job_event
from utils.exceptions import DocumentProcessingException
from models.base import ServiceType, JobStatus, ProcessingProgress
from models.document_models import DocumentProcessingRequest, DocumentResults

from .processor import (
    extract_text_content, 
    calculate_confidence_statistics,
    save_raw_response,
    extract_page_metadata,
    create_table_data
)
from .table_extractor import process_tables, create_excel_from_tables
from .confidence_dashboard import create_confidence_dashboard

logger = get_logger(__name__)


class DocumentIntelligenceService:
    """Service for document intelligence operations."""
    
    def __init__(self):
        """Initialize the service with Azure clients."""
        self.config = get_config()
        self.client = get_document_intelligence_client()
        self.file_handler = get_file_handler()
        self.job_manager = get_job_manager()
        
        # Always use prebuilt-layout model
        self.model = 'layout'
    
    async def analyze_document(
        self,
        file_path: str,
        job_id: str,
        model_id: str = None,
        extract_tables: bool = True,
        extract_text: bool = True,
        output_format: str = "markdown",
        progress_callback: Optional[Callable] = None
    ) -> DocumentResults:
        """
        Analyze a document using Azure Document Intelligence.
        
        Args:
            file_path: Path to the document file
            job_id: Job ID for tracking
            model_id: Analysis model to use (ignored, always uses layout)
            extract_tables: Whether to extract tables
            extract_text: Whether to extract text
            output_format: Output format (markdown or json)
            progress_callback: Callback for progress updates
        
        Returns:
            DocumentResults with processed data
        """
        with PerformanceTimer(logger, f"analyze_document_{self.model}"):
            try:
                start_time = datetime.utcnow()
                
                # Update progress
                if progress_callback:
                    await progress_callback(10, "Starting document analysis...")
                
                # Read document content
                with open(file_path, "rb") as document:
                    document_content = document.read()
                
                if progress_callback:
                    await progress_callback(20, "Sending document to Azure...")
                
                # Analyze document with Azure
                poller = self.client.begin_analyze_document(
                    "prebuilt-layout",  # Always use layout model
                    body=AnalyzeDocumentRequest(bytes_source=document_content),
                    output_content_format=DocumentContentFormat.MARKDOWN if output_format == "markdown" else None
                )
                
                # Poll for completion with progress updates
                result = await self._poll_for_result(poller, progress_callback)
                
                if progress_callback:
                    await progress_callback(70, "Processing analysis results...")
                
                # Process the results
                document_results = await self._process_analysis_result(
                    result, 
                    file_path, 
                    job_id,
                    extract_tables,
                    extract_text,
                    output_format
                )
                
                # Calculate processing time
                processing_time = (datetime.utcnow() - start_time).total_seconds()
                document_results.processing_time_seconds = processing_time
                
                if progress_callback:
                    await progress_callback(100, "Document analysis complete")
                
                log_job_event(
                    logger,
                    job_id,
                    "document_analyzed",
                    message=f"Document analyzed: {document_results.total_pages} pages, {len(document_results.extracted_tables)} tables extracted in {processing_time:.1f}s"
                )
                
                return document_results
                
            except Exception as e:
                logger.error(f"Document analysis failed: {str(e)}")
                raise DocumentProcessingException(
                    message=f"Failed to analyze document: {str(e)}",
                    job_id=job_id,
                    file_path=file_path
                )
    
    async def _poll_for_result(self, poller, progress_callback: Optional[Callable] = None):
        """Poll for analysis result with progress updates."""
        progress = 30
        
        while not poller.done():
            await asyncio.sleep(2)  # Poll every 2 seconds
            progress = min(progress + 5, 65)  # Increment progress up to 65%
            
            if progress_callback:
                await progress_callback(progress, "Document analysis in progress...")
        
        return poller.result()
    
    async def _process_analysis_result(
        self,
        result,
        file_path: str,
        job_id: str,
        extract_tables: bool,
        extract_text: bool,
        output_format: str
    ) -> DocumentResults:
        """Process the Azure analysis result into our format."""
        document_name = Path(file_path).name
        doc_name, file_ext = os.path.splitext(document_name)
        file_ext = file_ext.strip('.').lower() if file_ext else "pdf"
        
        # Save raw Azure response for debugging
        azure_response_path = await save_raw_response(result, doc_name, job_id, self.file_handler)
        
        # Process tables
        csv_files = []
        csv_files_info = []
        markdown_tables = []
        
        if extract_tables:
            csv_files, markdown_tables, csv_files_info = await process_tables(
                result, doc_name, file_ext, self.file_handler
            )
        
        # Extract text content
        markdown_content = None
        md_pages = []
        
        if extract_text and output_format == "markdown":
            markdown_content, md_pages = await extract_text_content(
                result, markdown_tables, doc_name, file_ext, self.file_handler
            )
        
        # Calculate confidence statistics
        confidence_stats = calculate_confidence_statistics(result)
        
        # Create confidence dashboard
        dashboard_path = None
        if confidence_stats["document_level"]["total_words"] > 0:
            dashboard_path = await create_confidence_dashboard(
                result, doc_name, confidence_stats, self.file_handler
            )
        
        # Create Excel file with all tables
        excel_file = None
        if csv_files:
            excel_file = await create_excel_from_tables(
                csv_files_info, doc_name, self.file_handler
            )
        
        # Extract page metadata
        pages_data, total_pages = extract_page_metadata(result)
        
        return DocumentResults(
            document_name=document_name,
            total_pages=total_pages,
            extracted_tables=create_table_data(csv_files_info),
            markdown_content=markdown_content,
            confidence_stats=confidence_stats,
            csv_files=csv_files,
            excel_file=excel_file,
            confidence_dashboard=dashboard_path,
            md_pages=md_pages,
            processing_time_seconds=0.0,  # Will be set by caller
            azure_response_json=azure_response_path
        )
    
    async def create_results_package(
        self,
        job_id: str,
        results: DocumentResults,
        original_filename: str = None
    ) -> str:
        """Create a ZIP package with all results."""
        files_to_zip = []
        
        # Use original filename if provided, otherwise use document name
        base_name = original_filename or results.document_name
        if base_name:
            base_name = os.path.splitext(base_name)[0]
        else:
            base_name = job_id
        
        # Add CSV files to csv/ directory
        if results.csv_files:
            for csv_file in results.csv_files:
                if os.path.exists(csv_file):
                    files_to_zip.append(csv_file)
        
        # Add Excel file to root
        if results.excel_file and os.path.exists(results.excel_file):
            files_to_zip.append(results.excel_file)
        
        # Create and add main markdown file to md/
        if results.markdown_content:
            md_path = await self.file_handler.create_temp_file(
                results.markdown_content.encode('utf-8'),
                f"{base_name}.md"
            )
            files_to_zip.append(md_path)
        
        # Add individual page markdown files to md/md_pages/
        if results.md_pages:
            for md_page in results.md_pages:
                if os.path.exists(md_page):
                    files_to_zip.append(md_page)
        
        # Add confidence dashboard to root
        if results.confidence_dashboard and os.path.exists(results.confidence_dashboard):
            files_to_zip.append(results.confidence_dashboard)
        
        # Add Azure response JSON to root
        if results.azure_response_json and os.path.exists(results.azure_response_json):
            files_to_zip.append(results.azure_response_json)
        
        # Create analysis summary JSON in root
        character_count = len(results.markdown_content) if results.markdown_content else 0
        summary = {
            "document_name": results.document_name,
            "total_pages": results.total_pages,
            "table_count": len(results.extracted_tables),
            "character_count": character_count,
            "confidence_stats": results.confidence_stats,
            "processing_time_seconds": results.processing_time_seconds,
            "analysis_timestamp": datetime.utcnow().isoformat(),
            "files_included": {
                "csv_files": len(results.csv_files) if results.csv_files else 0,
                "excel_file": bool(results.excel_file),
                "markdown_file": bool(results.markdown_content),
                "page_markdown_files": len(results.md_pages) if results.md_pages else 0,
                "confidence_dashboard": bool(results.confidence_dashboard),
                "azure_response_json": bool(results.azure_response_json)
            }
        }
        
        summary_path = await self.file_handler.create_temp_file(
            json.dumps(summary, indent=2).encode('utf-8'),
            "analysis_summary.json"
        )
        files_to_zip.append(summary_path)
        
        # Create ZIP package
        zip_filename = f"{job_id}_results.zip"
        zip_path = await self.file_handler.zip_files(
            files_to_zip,
            zip_filename,
            job_id
        )
        
        return zip_path
    
    async def get_supported_formats(self) -> Dict[str, Any]:
        """Get supported document formats and models."""
        return {
            "formats": [
                {
                    "extension": ".pdf",
                    "mime_type": "application/pdf",
                    "description": "PDF documents",
                    "max_size_mb": 50
                },
                {
                    "extension": ".docx",
                    "mime_type": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                    "description": "Word documents",
                    "max_size_mb": 50
                },
                {
                    "extension": ".jpg",
                    "mime_type": "image/jpeg",
                    "description": "JPEG images",
                    "max_size_mb": 50
                },
                {
                    "extension": ".png",
                    "mime_type": "image/png",
                    "description": "PNG images",
                    "max_size_mb": 50
                },
                {
                    "extension": ".tiff",
                    "mime_type": "image/tiff",
                    "description": "TIFF images",
                    "max_size_mb": 50
                },
                {
                    "extension": ".bmp",
                    "mime_type": "image/bmp",
                    "description": "BMP images",
                    "max_size_mb": 50
                }
            ],
            "models": [
                {
                    "id": "layout",
                    "name": "Layout Analysis",
                    "description": "Extract text, tables, and layout structure",
                    "cost_per_thousand_pages": 10.00
                }
            ],
            "max_file_size_mb": 50,
            "max_pages": 500
        }


# Global service instance
_document_intelligence_service: Optional[DocumentIntelligenceService] = None


def get_document_intelligence_service() -> DocumentIntelligenceService:
    """Get global document intelligence service instance."""
    global _document_intelligence_service
    if _document_intelligence_service is None:
        _document_intelligence_service = DocumentIntelligenceService()
    return _document_intelligence_service