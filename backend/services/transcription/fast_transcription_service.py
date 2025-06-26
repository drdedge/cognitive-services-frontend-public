#backend/services/transcription/fast_transcription_service.py
"""
Fast transcription service with Azure Speech Services REST API
=============================================================

Implements direct integration with Azure Speech Services fast transcription endpoint,
providing high-performance audio transcription with speaker diarization and
comprehensive format support:

## Key Features:
----------------
- Direct REST API integration with Azure Speech Services
- Support for 11 audio formats (WAV, MP3, OPUS, OGG, etc)
- Files up to 300MB and 2 hours duration
- Speaker diarization with up to 20 speakers
- Real-time progress tracking
- Automatic language detection option
- Cost estimation based on audio duration

## Technical Details:
--------------------
- Uses Azure Cognitive Services Speech API v2024-11-15
- Asynchronous HTTP requests with aiohttp
- Multipart form data for efficient file upload
- Comprehensive error handling and validation

"""

import os
import json
import asyncio
import aiohttp
from typing import Dict, Any, Optional, Callable, List, Tuple
from datetime import datetime
from pathlib import Path

from utils.config import get_config
from utils.logging import get_logger
from utils.exceptions import AzureServiceException, FileException

logger = get_logger(__name__)


class FastTranscriptionService:
    """Service for fast audio transcription using Azure Speech REST API."""
    
    # Supported audio formats
    SUPPORTED_FORMATS = {
        '.wav': 'audio/wav',
        '.mp3': 'audio/mpeg',
        '.opus': 'audio/opus',
        '.ogg': 'audio/ogg',
        '.flac': 'audio/flac',
        '.wma': 'audio/x-ms-wma',
        '.aac': 'audio/aac',
        '.amr': 'audio/amr',
        '.webm': 'audio/webm',
        '.spx': 'audio/speex',
        '.speex': 'audio/speex'
    }
    
    # API constraints
    MAX_FILE_SIZE_MB = 300
    MAX_DURATION_HOURS = 2
    
    def __init__(self):
        """Initialize the service with Azure credentials."""
        self.config = get_config()
        self.speech_key = self.config.speech_key
        self.speech_region = self.config.speech_region
        
        if not self.speech_key or not self.speech_region:
            raise ValueError("Azure Speech Services credentials not configured")
        
        # API endpoint - using the correct cognitive services endpoint
        self.api_endpoint = f"https://{self.speech_region}.api.cognitive.microsoft.com/speechtotext/transcriptions:transcribe"
        self.api_version = "2024-11-15"
    
    async def validate_audio_file(self, file_path: str) -> Tuple[bool, str, Dict[str, Any]]:
        """
        Validate audio file meets API requirements.
        
        Args:
            file_path: Path to audio file
            
        Returns:
            Tuple of (is_valid, error_message, file_info)
        """
        try:
            file_stat = os.stat(file_path)
            file_size_mb = file_stat.st_size / (1024 * 1024)
            file_ext = Path(file_path).suffix.lower()
            
            # Check file size
            if file_size_mb > self.MAX_FILE_SIZE_MB:
                return False, f"File size {file_size_mb:.1f}MB exceeds maximum of {self.MAX_FILE_SIZE_MB}MB", {}
            
            # Check file format
            if file_ext not in self.SUPPORTED_FORMATS:
                return False, f"File format {file_ext} not supported. Supported formats: {', '.join(self.SUPPORTED_FORMATS.keys())}", {}
            
            file_info = {
                'size_mb': file_size_mb,
                'format': file_ext,
                'mime_type': self.SUPPORTED_FORMATS[file_ext],
                'filename': os.path.basename(file_path)
            }
            
            # Note: Duration check would require parsing the audio file
            # The API will reject files > 2 hours automatically
            
            return True, "", file_info
            
        except Exception as e:
            logger.error(f"Error validating audio file: {e}")
            return False, f"Error validating file: {str(e)}", {}
    
    async def transcribe_audio(
        self,
        file_path: str,
        job_id: str,
        language: str = "en-US",
        enable_diarization: bool = True,
        max_speakers: int = 20,
        progress_callback: Optional[Callable] = None
    ) -> Dict[str, Any]:
        """
        Transcribe audio file using fast transcription API.
        
        Args:
            file_path: Path to audio file
            job_id: Job ID for tracking
            language: Language code (e.g., "en-US")
            enable_diarization: Enable speaker diarization
            max_speakers: Maximum number of speakers to identify
            progress_callback: Progress callback function
            
        Returns:
            Transcription results from Azure API
        """
        # Validate file
        is_valid, error_msg, file_info = await self.validate_audio_file(file_path)
        if not is_valid:
            raise FileException(
                message=error_msg,
                error_code="INVALID_AUDIO_FILE",
                details={"file_path": file_path, "operation": "validate"}
            )
        
        if progress_callback:
            await progress_callback(10, "Audio file validated, preparing for transcription...")
        
        try:
            # Prepare the multipart form data
            url = f"{self.api_endpoint}?api-version={self.api_version}"
            headers = {
                'Ocp-Apim-Subscription-Key': self.speech_key
            }
            
            # Definition for the transcription request
            definition = {
                "locales": [language],
                "diarization": {
                    "enabled": enable_diarization,
                    "maxSpeakers": max_speakers
                }
            }
            
            if progress_callback:
                await progress_callback(20, f"Uploading {file_info['size_mb']:.1f}MB audio file...")
            
            # Create form data
            async with aiohttp.ClientSession() as session:
                with open(file_path, 'rb') as audio_file:
                    form_data = aiohttp.FormData()
                    form_data.add_field(
                        'audio',
                        audio_file,
                        filename=file_info['filename'],
                        content_type=file_info['mime_type']
                    )
                    form_data.add_field(
                        'definition',
                        json.dumps(definition),
                        content_type='application/json'
                    )
                    
                    if progress_callback:
                        await progress_callback(30, "Sending request to Azure Speech Services...")
                    
                    # Send request
                    start_time = datetime.utcnow()
                    async with session.post(url, headers=headers, data=form_data) as response:
                        if response.status != 200:
                            error_text = await response.text()
                            logger.error(f"Transcription API error: {response.status} - {error_text}")
                            
                            # Create a custom exception with the error details
                            error_exc = Exception(f"API returned {response.status}: {error_text}")
                            raise AzureServiceException(
                                message=f"Transcription failed with status {response.status}",
                                service="Speech Services",
                                azure_error=error_exc
                            )
                        
                        if progress_callback:
                            await progress_callback(80, "Processing transcription results...")
                        
                        # Parse response
                        result = await response.json()
                        processing_time = (datetime.utcnow() - start_time).total_seconds()
                        
                        # Add metadata
                        result['metadata'] = {
                            'job_id': job_id,
                            'file_info': file_info,
                            'language': language,
                            'diarization_enabled': enable_diarization,
                            'processing_time_seconds': processing_time,
                            'processed_at': datetime.utcnow().isoformat()
                        }
                        
                        if progress_callback:
                            await progress_callback(100, "Transcription complete")
                        
                        logger.info(f"Transcription completed for job {job_id} in {processing_time:.1f}s")
                        return result
                        
        except aiohttp.ClientError as e:
            logger.error(f"Network error during transcription: {e}")
            raise AzureServiceException(
                message="Network error during transcription",
                service="Speech Services",
                azure_error=e
            )
        except AzureServiceException:
            # Re-raise AzureServiceException as-is
            raise
        except Exception as e:
            logger.error(f"Unexpected error during transcription: {e}")
            raise AzureServiceException(
                message=f"Transcription failed: {str(e)}",
                service="Speech Services",
                azure_error=e
            )
    
    async def estimate_cost(
        self,
        duration_seconds: float,
        file_size_mb: float = 0
    ) -> Dict[str, Any]:
        """
        Estimate transcription cost.
        
        Args:
            duration_seconds: Audio duration in seconds
            file_size_mb: File size in MB (used if duration unknown)
            
        Returns:
            Cost estimation details
        """
        # If duration not provided, estimate from file size
        if duration_seconds == 0 and file_size_mb > 0:
            # Rough estimate: 1MB ≈ 1 minute for typical audio
            duration_seconds = file_size_mb * 60
        
        # Azure Speech pricing: $1.00 per audio hour
        cost_per_hour = 1.00
        hours = max(1/60, duration_seconds / 3600)  # Minimum 1 minute billing
        
        estimated_cost = hours * cost_per_hour
        
        return {
            "estimated_cost_usd": round(estimated_cost, 4),
            "duration_seconds": duration_seconds,
            "duration_minutes": duration_seconds / 60,
            "duration_hours": hours,
            "cost_per_hour": cost_per_hour,
            "file_size_mb": file_size_mb
        }
    
    def get_supported_formats(self) -> List[Dict[str, str]]:
        """Get list of supported audio formats."""
        return [
            {
                "extension": ext,
                "mime_type": mime_type,
                "description": self._get_format_description(ext)
            }
            for ext, mime_type in self.SUPPORTED_FORMATS.items()
        ]
    
    def _get_format_description(self, extension: str) -> str:
        """Get human-readable description for audio format."""
        descriptions = {
            '.wav': 'Waveform Audio File',
            '.mp3': 'MP3 Audio',
            '.opus': 'Opus Audio Codec',
            '.ogg': 'OGG Vorbis Audio',
            '.flac': 'Free Lossless Audio Codec',
            '.wma': 'Windows Media Audio',
            '.aac': 'Advanced Audio Coding',
            '.amr': 'Adaptive Multi-Rate Audio',
            '.webm': 'WebM Audio',
            '.spx': 'Speex Audio',
            '.speex': 'Speex Audio'
        }
        return descriptions.get(extension, 'Audio File')


# Global service instance
_fast_transcription_service: Optional[FastTranscriptionService] = None


def get_fast_transcription_service() -> FastTranscriptionService:
    """Get global fast transcription service instance."""
    global _fast_transcription_service
    if _fast_transcription_service is None:
        _fast_transcription_service = FastTranscriptionService()
    return _fast_transcription_service