#backend/api/document_intelligence.py
"""
Document Intelligence API endpoints with Azure Document Intelligence – FastAPI integration
========================================================================================

Provides comprehensive REST API endpoints for document analysis and processing
using Azure Document Intelligence service. Enables extraction of text, tables,
and structural information from various document formats:

## Key Features:
-----------------
- Multi-format document processing (PDF, DOCX, images)
- Table extraction to CSV/Excel with confidence scoring
- Text extraction with markdown formatting
- Real-time progress updates via WebSocket
- Batch processing support for multiple documents
- Cost estimation before processing
- Async background task processing
- Comprehensive error handling and job management

This module serves as the API layer between the frontend and the Document
Intelligence service, handling file uploads, job creation, progress tracking,
and result delivery. All processing happens asynchronously to ensure responsive
API performance.

## API Endpoints:
----------------
- POST /process - Main document processing endpoint
- GET /status/{job_id} - Check processing status
- POST /estimate-cost - Calculate processing costs
- GET /results/{job_id} - Download processed results
- GET /results/{job_id}/metadata - Get result metadata
- POST /cancel/{job_id} - Cancel running jobs
- GET /supported-formats - List supported file types
- GET /models - Get available analysis models
- POST /batch - Process multiple documents
- GET /health - Service health check
"""
import json
import os
from typing import List, Dict, Any
from fastapi import APIRouter, UploadFile, File, HTTPException, BackgroundTasks, Form
from fastapi.responses import FileResponse
from datetime import datetime

from services.document_intelligence import get_document_intelligence_service
from services.websocket import get_websocket_manager
from utils.file_handler import get_file_handler, upload_file
from utils.job_manager import get_job_manager
from utils.logging import get_logger
from models.base import ServiceType, JobStatus, ProcessingProgress, create_success_response, create_error_response, ErrorDetails

logger = get_logger(__name__)
router = APIRouter()

# Initialize services
doc_service = get_document_intelligence_service()
websocket_manager = get_websocket_manager()
file_handler = get_file_handler()
job_manager = get_job_manager()


def serialize_response(response):
    """Helper to serialize response objects to dict."""
    try:
        return response.model_dump(mode='json')
    except AttributeError:
        return json.loads(response.json())


@router.post("/process")
async def process_document(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    model_id: str = Form(default="layout"),
    extract_tables: bool = Form(default=True),
    extract_text: bool = Form(default=True),
    output_format: str = Form(default="markdown")
):
    """Process a document using Azure Document Intelligence."""
    job = None
    try:
        # Create job
        job = await job_manager.create_job(
            service_type=ServiceType.DOCUMENT_INTELLIGENCE,
            parameters={
                "model_id": model_id,
                "extract_tables": extract_tables,
                "extract_text": extract_text,
                "output_format": output_format,
                "filename": file.filename
            }
        )
        
        logger.info(f"Created document processing job: {job.job_id}")
        
        # Upload file
        file_metadata = await upload_file(
            file=file,
            job_id=job.job_id,
            service_type=ServiceType.DOCUMENT_INTELLIGENCE
        )
        
        # Start processing in background
        background_tasks.add_task(
            process_document_task,
            job.job_id,
            file_metadata.storage_path,
            model_id,
            extract_tables,
            extract_text,
            output_format
        )
        
        return serialize_response(create_success_response(
            data={
                "job_id": job.job_id,
                "status": job.status.value,
                "message": "Document processing started",
                "file_info": {
                    "filename": file_metadata.filename,
                    "size_bytes": file_metadata.size_bytes,
                    "mime_type": file_metadata.mime_type
                }
            }
        ))
        
    except Exception as e:
        logger.error(f"Error creating document processing job: {str(e)}")
        
        # Clean up job if it was created
        if job:
            try:
                await job_manager.update_job_status(job.job_id, JobStatus.FAILED)
            except:
                pass
        
        return serialize_response(create_error_response(
            error_code="JOB_CREATION_FAILED",
            error_message=f"Failed to create processing job: {str(e)}"
        ))


async def process_document_task(
    job_id: str,
    file_storage_path: str,
    model_id: str,
    extract_tables: bool,
    extract_text: bool,
    output_format: str
):
    """Background task for document processing."""
    local_file_path = None
    try:
        # Update job status
        await job_manager.update_job_status(
            job_id,
            JobStatus.PROCESSING,
            ProcessingProgress(
                current_step="initializing",
                progress_percentage=0,
                message="Initializing document processing..."
            )
        )
        
        # Download file
        local_file_path = await file_handler.download_file(file_storage_path)
        
        # Progress callback
        async def progress_callback(percentage: int, message: str):
            progress = ProcessingProgress(
                current_step="processing",
                progress_percentage=percentage,
                message=message
            )
            await job_manager.update_job_status(job_id, JobStatus.PROCESSING, progress)
            
            # Send WebSocket update
            try:
                await websocket_manager.broadcast_job_update(
                    job_id=job_id,
                    status=JobStatus.PROCESSING,
                    progress=progress
                )
            except Exception as e:
                logger.warning(f"Failed to send WebSocket update: {e}")
        
        # Process document
        results = await doc_service.analyze_document(
            file_path=local_file_path,
            job_id=job_id,
            model_id=model_id,
            extract_tables=extract_tables,
            extract_text=extract_text,
            output_format=output_format,
            progress_callback=progress_callback
        )
        
        # Create results package with original filename
        job = await job_manager.get_job(job_id)
        original_filename = job.parameters.get('filename')
        results_zip_path = await doc_service.create_results_package(job_id, results, original_filename)
        
        # Store key results metadata in job parameters for later retrieval
        job = await job_manager.get_job(job_id)
        
        # Store the ZIP path for download
        job.parameters['results_zip_path'] = results_zip_path
        
        # Calculate character count from markdown content
        character_count = len(results.markdown_content) if results.markdown_content else 0
        
        job.parameters['results_metadata'] = {
            'markdown_content': results.markdown_content,
            'total_pages': results.total_pages,
            'table_count': len(results.extracted_tables),
            'character_count': character_count,
            'tables': [{
                'page_number': table.page_number,
                'table_index': table.table_index,
                'rows': table.rows,
                'columns': table.columns
            } for table in results.extracted_tables],
            'confidence_stats': results.confidence_stats,
            'word_count': results.confidence_stats.get('document_level', {}).get('total_words', 0),
            'processing_time_seconds': results.processing_time_seconds
        }
        
        # Update job as completed
        await job_manager.update_job_status(
            job_id,
            JobStatus.COMPLETED,
            ProcessingProgress(
                current_step="completed",
                progress_percentage=100,
                message="Document processing completed successfully"
            )
        )
        
        # Notify completion with character count
        try:
            await websocket_manager.broadcast_job_completion(
                job_id=job_id,
                results_url=f"/api/document-intelligence/results/{job_id}",
                processing_time_seconds=results.processing_time_seconds,
                data={'character_count': character_count}
            )
        except Exception as e:
            logger.warning(f"Failed to send completion notification: {e}")
        
        logger.info(f"Document processing completed: {job_id}")
        
    except Exception as e:
        logger.error(f"Document processing failed for job {job_id}: {str(e)}")
        
        # Update job as failed
        await job_manager.update_job_status(
            job_id,
            JobStatus.FAILED,
            error=create_error_response(
                error_code="PROCESSING_FAILED",
                error_message=str(e)
            ).error
        )
        
        # Notify failure
        try:
            await websocket_manager.broadcast_error(
                error=ErrorDetails(
                    code="PROCESSING_FAILED",
                    message=str(e)
                ),
                job_id=job_id
            )
        except Exception as ws_error:
            logger.warning(f"Failed to send error notification: {ws_error}")
    
    finally:
        # Cleanup
        if local_file_path and os.path.exists(local_file_path):
            try:
                os.remove(local_file_path)
            except:
                pass


@router.get("/status/{job_id}")
async def get_processing_status(job_id: str):
    """Get the status of a document processing job."""
    try:
        job = await job_manager.get_job(job_id)
        
        return serialize_response(create_success_response(
            data={
                "job_id": job.job_id,
                "status": job.status.value,
                "created_at": job.created_at.isoformat(),
                "updated_at": job.updated_at.isoformat(),
                "progress": job.progress.dict() if job.progress else None,
                "error": job.error.dict() if job.error else None
            }
        ))
        
    except Exception as e:
        logger.error(f"Error getting job status {job_id}: {str(e)}")
        return serialize_response(create_error_response(
            error_code="JOB_NOT_FOUND",
            error_message=f"Job not found: {job_id}"
        ))


@router.post("/estimate-cost")
async def estimate_cost(request: Dict[str, Any]):
    """Estimate the cost of processing a document."""
    try:
        cost_estimate = await doc_service.estimate_cost(
            file_size_bytes=request.get("file_size", 0),
            file_type=request.get("file_type", "pdf"),
            model_id=request.get("model_id", "layout"),
            extract_tables=request.get("extract_tables", True)
        )
        
        return serialize_response(create_success_response(
            data=cost_estimate,
            message="Cost estimation completed"
        ))
        
    except Exception as e:
        logger.error(f"Error estimating cost: {str(e)}")
        return serialize_response(create_error_response(
            error_code="COST_ESTIMATION_FAILED",
            error_message=f"Failed to estimate cost: {str(e)}"
        ))


@router.get("/results/{job_id}")
async def download_results(job_id: str):
    """Download processed document results as ZIP."""
    try:
        job = await job_manager.get_job(job_id)
        
        if job.status != JobStatus.COMPLETED:
            raise HTTPException(
                status_code=400,
                detail=f"Job not completed. Current status: {job.status.value}"
            )
        
        # Check if we have the results path stored in job parameters
        results_zip_path = job.parameters.get('results_zip_path')
        
        if results_zip_path:
            # Download from blob storage to temp file
            import tempfile
            import aiofiles
            
            try:
                # Download the ZIP file from blob storage
                temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.zip')
                temp_path = temp_file.name
                temp_file.close()
                
                # Download from blob storage
                await file_handler.download_to_path(results_zip_path, temp_path)
                
                # Return the file and ensure cleanup
                def cleanup():
                    try:
                        os.unlink(temp_path)
                    except:
                        pass
                
                background_tasks = BackgroundTasks()
                background_tasks.add_task(cleanup)
                
                return FileResponse(
                    path=temp_path,
                    filename=f"{job_id}_document_analysis_results.zip",
                    media_type="application/zip",
                    background=background_tasks
                )
            except Exception as e:
                logger.error(f"Failed to download from blob storage: {e}")
                # Fall back to local file search
        
        # Fallback: Look for local file (for backwards compatibility)
        temp_dir = file_handler.temp_dir
        import glob
        pattern = os.path.join(temp_dir, f"*_{job_id}_results.zip")
        zip_files = glob.glob(pattern)
        
        if not zip_files:
            raise HTTPException(
                status_code=404,
                detail="Results file not found"
            )
        
        # Use the most recent file if multiple found
        results_path = max(zip_files, key=os.path.getctime)
        
        return FileResponse(
            path=results_path,
            filename=f"{job_id}_document_analysis_results.zip",
            media_type="application/zip"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error downloading results for job {job_id}: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to download results: {str(e)}"
        )


@router.get("/results/{job_id}/metadata")
async def get_results_metadata(job_id: str):
    """Get metadata about processing results."""
    try:
        job = await job_manager.get_job(job_id)
        
        if job.status != JobStatus.COMPLETED:
            return serialize_response(create_error_response(
                error_code="JOB_NOT_COMPLETED",
                error_message=f"Job not completed. Current status: {job.status.value}"
            ))
        
        # Get stored results metadata from job parameters
        results_metadata = job.parameters.get('results_metadata', {})
        
        # Build response with all the data the frontend expects
        metadata = {
            "job_id": job_id,
            "document_name": job.parameters.get("filename", "unknown"),
            "processing_model": job.parameters.get("model_id", "layout"),
            "extract_tables": job.parameters.get("extract_tables", False),
            "extract_text": job.parameters.get("extract_text", False),
            "completed_at": job.completed_at.isoformat() if job.completed_at else None,
            "processing_time_seconds": results_metadata.get('processing_time_seconds', job.duration_seconds),
            "results_available": True,
            # Add the actual results data
            "markdown_content": results_metadata.get('markdown_content', ''),
            "total_pages": results_metadata.get('total_pages', 0),
            "table_count": results_metadata.get('table_count', 0),
            "character_count": results_metadata.get('character_count', 0),
            "tables": results_metadata.get('tables', []),
            "confidence_stats": results_metadata.get('confidence_stats', {}),
            "word_count": results_metadata.get('word_count', 0)
        }
        
        return serialize_response(create_success_response(
            data=metadata,
            message="Results metadata retrieved successfully"
        ))
        
    except Exception as e:
        logger.error(f"Error getting results metadata for job {job_id}: {str(e)}")
        return serialize_response(create_error_response(
            error_code="METADATA_RETRIEVAL_FAILED",
            error_message=f"Failed to get results metadata: {str(e)}"
        ))


@router.post("/cancel/{job_id}")
async def cancel_job(job_id: str):
    """Cancel a processing job."""
    try:
        job = await job_manager.cancel_job(job_id, "User requested cancellation")
        
        # Notify WebSocket clients
        try:
            await websocket_manager.broadcast_job_update(
                job_id=job_id,
                status=JobStatus.CANCELLED,
                progress=ProcessingProgress(
                    current_step="cancelled",
                    progress_percentage=0,
                    message="Job cancelled by user request"
                )
            )
        except Exception as e:
            logger.warning(f"Failed to send cancellation notification: {e}")
        
        return serialize_response(create_success_response(
            data={
                "job_id": job_id,
                "status": job.status.value,
                "message": "Job cancelled successfully"
            }
        ))
        
    except Exception as e:
        logger.error(f"Error cancelling job {job_id}: {str(e)}")
        return serialize_response(create_error_response(
            error_code="CANCELLATION_FAILED",
            error_message=f"Failed to cancel job: {str(e)}"
        ))


@router.get("/supported-formats")
async def get_supported_formats():
    """Get list of supported document formats and analysis models."""
    try:
        formats_info = await doc_service.get_supported_formats()
        
        return serialize_response(create_success_response(
            data=formats_info,
            message="Supported formats retrieved successfully"
        ))
        
    except Exception as e:
        logger.error(f"Error getting supported formats: {str(e)}")
        return serialize_response(create_error_response(
            error_code="FORMATS_RETRIEVAL_FAILED",
            error_message=f"Failed to get supported formats: {str(e)}"
        ))


@router.get("/models")
async def get_analysis_models():
    """Get available analysis models with descriptions and pricing."""
    try:
        formats_info = await doc_service.get_supported_formats()
        
        return serialize_response(create_success_response(
            data={
                "models": formats_info.get("models", [])
            },
            message="Analysis models retrieved successfully"
        ))
        
    except Exception as e:
        logger.error(f"Error getting analysis models: {str(e)}")
        return serialize_response(create_error_response(
            error_code="MODELS_RETRIEVAL_FAILED",
            error_message=f"Failed to get analysis models: {str(e)}"
        ))


@router.post("/batch")
async def process_batch(
    background_tasks: BackgroundTasks,
    files: List[UploadFile] = File(...),
    model_id: str = Form(default="layout"),
    extract_tables: bool = Form(default=True),
    extract_text: bool = Form(default=True),
    output_format: str = Form(default="markdown")
):
    """Process multiple documents in batch."""
    try:
        job_ids = []
        failed_files = []
        
        for file in files:
            try:
                # Create job for each file
                job = await job_manager.create_job(
                    service_type=ServiceType.DOCUMENT_INTELLIGENCE,
                    parameters={
                        "model_id": model_id,
                        "extract_tables": extract_tables,
                        "extract_text": extract_text,
                        "output_format": output_format,
                        "filename": file.filename,
                        "batch_processing": True
                    }
                )
                
                # Upload file
                file_metadata = await upload_file(
                    file=file,
                    job_id=job.job_id,
                    service_type=ServiceType.DOCUMENT_INTELLIGENCE
                )
                
                # Start processing
                background_tasks.add_task(
                    process_document_task,
                    job.job_id,
                    file_metadata.storage_path,
                    model_id,
                    extract_tables,
                    extract_text,
                    output_format
                )
                
                job_ids.append({
                    "job_id": job.job_id,
                    "filename": file.filename,
                    "status": "queued"
                })
                
            except Exception as e:
                logger.error(f"Failed to process file {file.filename}: {str(e)}")
                failed_files.append({
                    "filename": file.filename,
                    "error": str(e)
                })
        
        batch_id = f"batch_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"
        
        return serialize_response(create_success_response(
            data={
                "batch_id": batch_id,
                "jobs": job_ids,
                "failed_files": failed_files,
                "total_files": len(files),
                "successful_files": len(job_ids),
                "failed_count": len(failed_files)
            },
            message=f"Batch processing initiated for {len(job_ids)} out of {len(files)} documents"
        ))
        
    except Exception as e:
        logger.error(f"Error creating batch processing: {str(e)}")
        return serialize_response(create_error_response(
            error_code="BATCH_CREATION_FAILED",
            error_message=f"Failed to create batch processing: {str(e)}"
        ))


@router.get("/health")
async def health_check():
    """Health check endpoint for the document intelligence service."""
    try:
        # Quick health check - just verify service is available
        is_healthy = doc_service is not None
        
        return serialize_response(create_success_response(
            data={
                "status": "healthy" if is_healthy else "unhealthy",
                "timestamp": datetime.utcnow().isoformat(),
                "service_available": is_healthy
            },
            message="Document Intelligence service health check"
        ))
        
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        return serialize_response(create_error_response(
            error_code="SERVICE_UNHEALTHY",
            error_message=f"Service health check failed: {str(e)}"
        ))