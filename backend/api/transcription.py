#backend/api/transcription.py
"""
Transcription API endpoints with Azure Speech Services – Fast transcription integration
=====================================================================================

Provides REST API endpoints for audio-to-text transcription using Azure Speech
Services' fast transcription API. Supports multiple audio formats with advanced
features like speaker diarization and language detection:

## Key Features:
-----------------
- Multi-format audio support (MP3, WAV, M4A, OGG)
- Speaker diarization with up to 20 speakers
- Automatic language detection support
- Real-time progress updates via WebSocket
- Cost estimation based on audio duration
- Async background processing for large files
- File size support up to 300MB
- Duration support up to 2 hours

This module handles the complete transcription workflow from file upload to
result delivery, integrating with job management and WebSocket services for
real-time status updates. All transcription happens asynchronously to maintain
API responsiveness.

## API Endpoints:
----------------
- POST /transcribe - Start audio transcription
- GET /status/{job_id} - Check transcription status
- POST /estimate-cost - Calculate transcription costs
- GET /results/{job_id} - Download transcription results
- GET /languages - List supported languages
- GET /supported-formats - List supported audio formats
"""

import os
import logging
import tempfile
from typing import Optional, Dict, Any
from fastapi import APIRouter, UploadFile, File, HTTPException, BackgroundTasks, Form
from fastapi.responses import FileResponse

from services.transcription import get_transcription_service
from services.storage import get_storage_service
from services.websocket import get_websocket_manager
from utils.job_manager import get_job_manager
from utils.file_handler import get_file_handler
from utils.logging import get_logger
from models.base import JobStatus, ServiceType, ProcessingProgress, ErrorDetails
from models.transcription_models import (
    TranscriptionRequest,
    TranscriptionResponse,
    TranscriptionStatus
)

logger = get_logger(__name__)
router = APIRouter()

# Get service instances
transcription_service = get_transcription_service()
storage_service = get_storage_service()
websocket_manager = get_websocket_manager()
job_manager = get_job_manager()
file_handler = get_file_handler()


@router.post("/transcribe")
async def transcribe_audio(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    language: str = Form(default="en-US"),
    enable_diarization: bool = Form(default=True),
    max_speakers: int = Form(default=20)
):
    """
    Transcribe audio file to text using fast transcription API.
    
    Args:
        file: Audio file to transcribe
        language: Language code for transcription
        enable_diarization: Enable speaker diarization
        max_speakers: Maximum number of speakers to identify
    
    Returns:
        Job information for tracking transcription progress
    """
    try:
        # Validate file
        supported_formats = transcription_service.get_supported_formats()
        file_ext = os.path.splitext(file.filename)[1].lower()
        
        if not any(fmt['extension'] == file_ext for fmt in supported_formats):
            allowed_types = [fmt['extension'] for fmt in supported_formats]
            raise HTTPException(
                status_code=400,
                detail=f"File type {file_ext} not supported. Allowed types: {', '.join(allowed_types)}"
            )
        
        # Check file size (300MB limit)
        file_content = await file.read()
        file_size_mb = len(file_content) / (1024 * 1024)
        
        if file_size_mb > 300:
            raise HTTPException(
                status_code=400,
                detail=f"File size {file_size_mb:.1f}MB exceeds maximum of 300MB"
            )
        
        # Create job
        job = await job_manager.create_job(
            service_type=ServiceType.TRANSCRIPTION,
            parameters={
                'file_name': file.filename,
                'file_size': len(file_content),
                'language': language,
                'enable_diarization': enable_diarization,
                'max_speakers': max_speakers
            }
        )
        
        # Save file temporarily
        temp_dir = tempfile.mkdtemp()
        temp_path = os.path.join(temp_dir, file.filename)
        
        with open(temp_path, 'wb') as f:
            f.write(file_content)
        
        # Upload to blob storage - FIX: Use job.job_id instead of job.id
        blob_path = await storage_service.upload_file_from_path(
            temp_path,
            f"transcription/{job.job_id}/{file.filename}"
        )
        
        # Start transcription in background - FIX: Use job.job_id instead of job.id
        background_tasks.add_task(
            _process_transcription_task,
            job.job_id,
            temp_path,
            blob_path,
            file.filename,
            language,
            enable_diarization,
            max_speakers
        )
        
        # FIX: Use job.job_id instead of job.id in response
        return {
            "job_id": job.job_id,
            "status": job.status,
            "message": "Transcription started",
            "created_at": job.created_at
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error starting transcription: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to start transcription: {str(e)}")


async def _process_transcription_task(
    job_id: str,
    temp_path: str,
    blob_path: str,
    original_filename: str,
    language: str,
    enable_diarization: bool,
    max_speakers: int
):
    """Background task for audio transcription."""
    try:
        # Update job status
        await job_manager.update_job_status(job_id, JobStatus.PROCESSING)
        
        # Progress callback
        async def progress_callback(percentage: int, message: str):
            progress = ProcessingProgress(
                current_step=message,
                progress_percentage=percentage,
                message=message
            )
            await websocket_manager.broadcast_job_update(
                job_id,
                JobStatus.PROCESSING,
                progress=progress
            )
        
        # Perform transcription
        result = await transcription_service.transcribe_audio(
            file_path=temp_path,
            job_id=job_id,
            original_filename=original_filename,
            language=language,
            enable_diarization=enable_diarization,
            max_speakers=max_speakers,
            progress_callback=progress_callback
        )
        
        # Update job with results
        # If JobManager has complete_job method, use it. Otherwise, update manually
        try:
            await job_manager.complete_job(
                job_id,
                results_path=result['results_path'],
                metadata={
                    'statistics': result['statistics'],
                    'speakers': result['speakers'],
                    'duration': result['duration'],
                    'language': result['language'],
                    'diarization_enabled': result['diarization_enabled']
                }
            )
        except AttributeError:
            # Fallback if complete_job method doesn't exist
            await job_manager.update_job_status(
                job_id,
                JobStatus.COMPLETED,
                progress=ProcessingProgress(
                    current_step="Transcription completed",
                    progress_percentage=100,
                    message="Processing complete"
                )
            )
            # Manually update job with results
            job = await job_manager.get_job(job_id)
            job.results_path = result['results_path']
            job.metadata = {
                'statistics': result['statistics'],
                'speakers': result['speakers'],
                'duration': result['duration'],
                'language': result['language'],
                'diarization_enabled': result['diarization_enabled']
            }
        
        # Broadcast completion
        await websocket_manager.broadcast_job_completion(
            job_id,
            results_url=f"/api/transcription/results/{job_id}",
            data={
                "word_count": result['statistics']['total_words'],
                "duration": result['duration'],
                "speakers": result['speakers']
            }
        )
        
    except Exception as e:
        logger.error(f"Transcription error for job {job_id}: {str(e)}")
        # Try to use fail_job if available, otherwise use update_job_status
        try:
            await job_manager.fail_job(job_id, str(e), "TRANSCRIPTION_ERROR")
        except AttributeError:
            # Fallback if fail_job method doesn't exist
            from models.base import ErrorDetails
            await job_manager.update_job_status(
                job_id, 
                JobStatus.FAILED,
                error=ErrorDetails(
                    error_code="TRANSCRIPTION_ERROR",
                    error_message=str(e),
                    severity="medium"
                )
            )
        
        await websocket_manager.broadcast_job_update(
            job_id,
            JobStatus.FAILED,
            error=ErrorDetails(
                error_code="TRANSCRIPTION_ERROR",
                error_message=str(e),
                severity="medium"
            )
        )
    finally:
        # Cleanup temp files
        if os.path.exists(temp_path):
            os.remove(temp_path)
        temp_dir = os.path.dirname(temp_path)
        if os.path.exists(temp_dir):
            try:
                os.rmdir(temp_dir)
            except:
                pass  # Directory might not be empty




@router.get("/languages")
async def get_supported_languages():
    """Get list of supported languages for transcription."""
    try:
        languages = transcription_service.get_supported_languages()
        return {"languages": languages}
        
    except Exception as e:
        logger.error(f"Error fetching languages: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/supported-formats")
async def get_supported_formats():
    """Get list of supported audio formats."""
    try:
        formats = transcription_service.get_supported_formats()
        return {
            "formats": formats,
            "max_file_size_mb": 300,
            "max_duration_hours": 2
        }
        
    except Exception as e:
        logger.error(f"Error fetching formats: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))




@router.post("/estimate-cost")
async def estimate_transcription_cost(request: dict):
    """Estimate the cost of transcription."""
    try:
        file_size_bytes = request.get("file_size_bytes", 0)
        duration_seconds = request.get("duration_seconds", 0)
        
        cost_estimate = await transcription_service.estimate_cost(
            file_size_bytes=file_size_bytes,
            duration_seconds=duration_seconds
        )
        
        return cost_estimate
        
    except Exception as e:
        logger.error(f"Error estimating cost: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/status/{job_id}")
async def get_transcription_status(job_id: str):
    """Get the status of a transcription job."""
    try:
        job = await job_manager.get_job(job_id)
        if not job:
            raise HTTPException(status_code=404, detail="Job not found")
        
        # FIX: Use job.job_id instead of job.id
        response = {
            "job_id": job.job_id,
            "status": job.status,
            "created_at": job.created_at,
            "updated_at": job.updated_at
        }
        
        if job.status == JobStatus.PROCESSING and job.progress:
            response["progress"] = job.progress
        
        if job.status == JobStatus.COMPLETED and hasattr(job, 'metadata') and job.metadata:
            response["metadata"] = job.metadata
        
        if job.status == JobStatus.FAILED and job.error:
            response["error"] = job.error
        
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting job status: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/results/{job_id}")
async def download_transcription_results(job_id: str):
    """Download transcription results as ZIP."""
    try:
        # Get job info
        job = await job_manager.get_job(job_id)
        if not job:
            raise HTTPException(status_code=404, detail="Job not found")
        
        if job.status != JobStatus.COMPLETED:
            raise HTTPException(
                status_code=400,
                detail=f"Job is not completed. Current status: {job.status}"
            )
        
        if not hasattr(job, 'results_path') or not job.results_path:
            raise HTTPException(status_code=404, detail="Results not found. Job may not have completed properly.")
        
        # Download from blob storage to temp file (consistent with Document Intelligence)
        import tempfile
        
        # Create a temporary file
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.zip')
        temp_path = temp_file.name
        temp_file.close()
        
        # Download from blob storage
        await file_handler.download_to_path(job.results_path, temp_path)
        
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
            filename=f"{job_id}_transcription.zip",
            media_type="application/zip",
            background=background_tasks
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error downloading results: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))