# backend/api/translation.py
"""
Translation API endpoints
=========================

Handles text and document translation using Azure Translator.
"""

import os
import logging
import tempfile
import shutil
from typing import List, Optional
from fastapi import APIRouter, UploadFile, File, HTTPException, BackgroundTasks, Form
from fastapi.responses import FileResponse

from services.translation import get_translation_service
from services.websocket import get_websocket_manager
from services.storage import get_storage_service
from utils.job_manager import get_job_manager
from utils.file_handler import get_file_handler
from utils.text_extractor import TextExtractor
from models.base import JobStatus, ServiceType, ProcessingProgress
from models.translation_models import (
    TranslationRequest,
    TranslationResponse,
    LanguageDetectionResponse,
    SupportedLanguagesResponse
)

logger = logging.getLogger(__name__)
router = APIRouter()

# Get service instances
try:
    translation_service = get_translation_service()
except Exception as e:
    logger.error(f"Failed to initialize translation service: {e}")
    translation_service = None

websocket_manager = get_websocket_manager()
storage_service = get_storage_service()
job_manager = get_job_manager()
file_handler = get_file_handler()


@router.post("/translate", response_model=TranslationResponse)
async def translate_text(request: TranslationRequest):
    """
    Translate text from source language to target language(s).
    
    Args:
        request: Translation request with text and language settings
    
    Returns:
        Translated text and metadata
    """
    try:
        result = await translation_service.translate_text(
            text=request.text,
            target_languages=request.target_languages,
            source_language=request.source_language
        )
        
        return TranslationResponse(
            original_text=request.text,
            translations=result["translations"],
            detected_language=result.get("detected_language")
        )
        
    except Exception as e:
        logger.error(f"Translation error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/translate-document")
async def translate_document(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    target_language: str = Form(...),
    source_language: Optional[str] = Form(default=None)
):
    """
    Translate a document file.
    
    Args:
        file: Document file to translate
        target_language: Target language code
        source_language: Source language code (auto-detect if not provided)
    
    Returns:
        Job information for tracking translation progress
    """
    try:
        # Validate file type
        allowed_types = ['.txt', '.docx', '.html', '.md']
        file_ext = os.path.splitext(file.filename)[1].lower()
        if file_ext not in allowed_types:
            raise HTTPException(
                status_code=400,
                detail=f"File type {file_ext} not supported. Allowed types: {', '.join(allowed_types)}"
            )
        
        # Read file content
        file_content = await file.read()
        
        # Create job
        job = await job_manager.create_job(
            service_type=ServiceType.TRANSLATION,
            parameters={
                'file_name': file.filename,
                'file_size': len(file_content),
                'target_language': target_language,
                'source_language': source_language or 'auto-detect'
            }
        )
        
        # Save file temporarily
        temp_dir = tempfile.mkdtemp()
        temp_path = os.path.join(temp_dir, file.filename)
        
        with open(temp_path, 'wb') as f:
            f.write(file_content)
        
        # Upload to blob storage
        blob_path = await storage_service.upload_file_from_path(
            temp_path,
            f"translation/{job.job_id}/{file.filename}"
        )
        
        # Start translation in background
        background_tasks.add_task(
            _process_translation_task,
            job.job_id,
            temp_path,
            blob_path,
            file.filename,
            target_language,
            source_language
        )
        
        return {
            "job_id": job.job_id,
            "status": job.status,
            "message": "Document translation started",
            "created_at": job.created_at
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error starting translation: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to start translation: {str(e)}")


async def _process_translation_task(
    job_id: str,
    temp_path: str,
    blob_path: str,
    original_filename: str,
    target_language: str,
    source_language: Optional[str]
):
    """Background task for document translation."""
    output_dir = None
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
        
        # Extract text content based on file type
        try:
            content = TextExtractor.extract_text(temp_path)
        except ValueError as e:
            # Unsupported file format
            raise Exception(f"Unsupported file format: {str(e)}")
        
        await progress_callback(10, "Document loaded, detecting language...")
        
        # Detect language if not provided
        if not source_language:
            detection = await translation_service.detect_language(content[:1000])
            source_language = detection['language']
            await progress_callback(20, f"Detected language: {source_language}")
        
        await progress_callback(30, f"Translating from {source_language} to {target_language}...")
        
        # Translate text
        result = await translation_service.translate_text(
            text=content,
            target_languages=[target_language],
            source_language=source_language
        )
        
        translated_text = result['translations'][0]['text']
        
        await progress_callback(70, "Creating translated document...")
        
        # Create output directory
        output_dir = tempfile.mkdtemp()
        
        # Save original document
        original_path = os.path.join(output_dir, f"original_{original_filename}")
        shutil.copy2(temp_path, original_path)
        
        # Save translated document in the same format as original
        file_ext = os.path.splitext(original_filename)[1].lower()
        base_name = os.path.splitext(original_filename)[0]
        translated_filename = f"translated_{target_language}_{original_filename}"
        translated_path = os.path.join(output_dir, translated_filename)
        
        # Save in appropriate format
        if file_ext == '.docx':
            # Save as DOCX
            from docx import Document
            doc = Document()
            # Split text into paragraphs
            paragraphs = translated_text.split('\n\n')
            for para in paragraphs:
                if para.strip():
                    doc.add_paragraph(para.strip())
            doc.save(translated_path)
        elif file_ext in ['.html', '.md']:
            # For HTML and Markdown, save as plain text but with original extension
            with open(translated_path, 'w', encoding='utf-8') as f:
                f.write(translated_text)
        else:
            # Default to text file
            with open(translated_path, 'w', encoding='utf-8') as f:
                f.write(translated_text)
        
        # Create metadata
        metadata = {
            "job_id": job_id,
            "source_language": source_language,
            "target_language": target_language,
            "original_filename": original_filename,
            "word_count": len(content.split()),
            "character_count": len(content),
            "translated_word_count": len(translated_text.split()),
            "translated_character_count": len(translated_text)
        }
        
        metadata_path = os.path.join(output_dir, "translation_metadata.json")
        import json
        with open(metadata_path, 'w') as f:
            json.dump(metadata, f, indent=2)
        
        await progress_callback(90, "Packaging results...")
        
        # Create ZIP file
        temp_dir = os.path.dirname(temp_path)
        zip_path = os.path.join(temp_dir, f"{job_id}_translation_results.zip")
        shutil.make_archive(zip_path.replace('.zip', ''), 'zip', output_dir)
        
        # Upload results to blob storage
        results_blob_path = f"translation/{job_id}/results.zip"
        await storage_service.upload_file_from_path(zip_path, results_blob_path)
        
        # Update job with results
        await job_manager.update_job_status(
            job_id,
            JobStatus.COMPLETED,
            progress=ProcessingProgress(
                current_step="Translation completed",
                progress_percentage=100,
                message="Processing complete"
            )
        )
        
        # Broadcast completion
        await websocket_manager.broadcast_job_completion(
            job_id,
            results_url=f"/api/translation/results/{job_id}",
            data={
                "word_count": metadata["translated_word_count"],
                "source_language": source_language,
                "target_language": target_language
            }
        )
        
        # Cleanup output directory
        if output_dir and os.path.exists(output_dir):
            shutil.rmtree(output_dir)
        
    except Exception as e:
        logger.error(f"Translation error for job {job_id}: {str(e)}")
        
        from models.base import ErrorDetails
        await job_manager.update_job_status(
            job_id,
            JobStatus.FAILED,
            error=ErrorDetails(
                error_code="TRANSLATION_ERROR",
                error_message=str(e),
                severity="medium"
            )
        )
        
        await websocket_manager.broadcast_job_update(
            job_id,
            JobStatus.FAILED,
            error=ErrorDetails(
                error_code="TRANSLATION_ERROR",
                error_message=str(e),
                severity="medium"
            )
        )
    finally:
        # Cleanup temp files
        try:
            if os.path.exists(temp_path):
                os.remove(temp_path)
            temp_dir = os.path.dirname(temp_path)
            if os.path.exists(temp_dir):
                try:
                    os.rmdir(temp_dir)
                except:
                    pass
            # Also cleanup output_dir if it wasn't cleaned up already
            if output_dir and os.path.exists(output_dir):
                shutil.rmtree(output_dir)
        except Exception as cleanup_error:
            logger.warning(f"Error during cleanup: {cleanup_error}")


@router.post("/detect-language", response_model=LanguageDetectionResponse)
async def detect_language(request: dict):
    """
    Detect the language of the provided text.
    
    Args:
        request: Dict containing text to analyze
    
    Returns:
        Detected language and confidence score
    """
    try:
        text = request.get("text", "")
        if not text:
            raise HTTPException(status_code=400, detail="Text is required")
            
        result = await translation_service.detect_language(text)
        return LanguageDetectionResponse(**result)
        
    except Exception as e:
        logger.error(f"Language detection error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/languages", response_model=SupportedLanguagesResponse)
async def get_supported_languages():
    """Get list of supported languages for translation."""
    if not translation_service:
        raise HTTPException(
            status_code=503,
            detail="Translation service is not available. Please check configuration."
        )
    
    try:
        languages = await translation_service.get_supported_languages()
        return SupportedLanguagesResponse(
            languages=languages,
            total=len(languages)
        )
        
    except Exception as e:
        logger.error(f"Error fetching languages: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/translate-batch")
async def translate_batch(
    texts: List[str],
    target_languages: List[str],
    source_language: Optional[str] = None
):
    """
    Translate multiple texts in batch.
    
    Args:
        texts: List of texts to translate
        target_languages: Target language codes
        source_language: Source language code (auto-detect if not provided)
    
    Returns:
        List of translation results
    """
    try:
        results = await translation_service.translate_batch(
            texts=texts,
            target_languages=target_languages,
            source_language=source_language
        )
        
        return {
            "translations": results,
            "total_processed": len(texts)
        }
        
    except Exception as e:
        logger.error(f"Batch translation error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/translate-text")
async def translate_text_simple(request: dict):
    """
    Simple text translation endpoint matching frontend expectations.
    
    Args:
        request: Dict with text, target_language, source_language
    """
    if not translation_service:
        raise HTTPException(
            status_code=503,
            detail="Translation service is not available. Please check configuration."
        )
    
    try:
        result = await translation_service.translate_text(
            text=request.get("text"),
            target_languages=[request.get("target_language")],
            source_language=request.get("source_language")
        )
        
        return {
            "translated_text": result["translations"][0]["text"],
            "source_language": result.get("detected_language"),
            "target_language": request.get("target_language"),
            "confidence": result.get("confidence", 1.0)
        }
        
    except Exception as e:
        logger.error(f"Text translation error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/estimate-cost")
async def estimate_translation_cost(request: dict):
    """Estimate the cost of translation."""
    text_length = len(request.get("text", ""))
    file_size = request.get("file_size", 0)
    
    # Hardcoded cost values for now
    if file_size > 0:
        # Document translation
        estimated_cost = 2.00
    else:
        # Text translation
        estimated_cost = 0.50
    
    # Still calculate character count for reference
    total_chars = text_length if text_length > 0 else max(1, file_size // 2)
    
    return {
        "estimated_cost": estimated_cost,
        "currency": "USD",
        "character_count": total_chars,
        "cost_per_character": 0.00002  # Reference value
    }


@router.get("/status/{job_id}")
async def get_translation_status(job_id: str):
    """Get the status of a translation job."""
    try:
        job = await job_manager.get_job(job_id)
        if not job:
            raise HTTPException(status_code=404, detail="Job not found")
        
        return {
            "job_id": job.job_id,
            "status": job.status,
            "progress": job.progress_percentage if hasattr(job, 'progress_percentage') else None,
            "message": job.current_step if hasattr(job, 'current_step') else "Processing",
            "created_at": job.created_at,
            "updated_at": job.updated_at
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting job status: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/results/{job_id}")
async def download_translation_results(job_id: str):
    """Download translation results."""
    try:
        # Get job details
        job = await job_manager.get_job(job_id)
        if not job:
            raise HTTPException(status_code=404, detail="Job not found")
        
        if job.status != JobStatus.COMPLETED:
            raise HTTPException(
                status_code=400,
                detail=f"Job is not completed. Current status: {job.status}"
            )
        
        # Download from blob storage
        blob_path = f"translation/{job_id}/results.zip"
        temp_path = f"/tmp/{job_id}_results.zip"
        
        await storage_service.download_to_path(blob_path, temp_path)
        
        return FileResponse(
            path=temp_path,
            filename=f"{job_id}_translation_results.zip",
            media_type="application/zip"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error downloading results: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))