#backend/services/transcription/service.py
"""
Main transcription service orchestrator with Azure Speech Services
================================================================

Orchestrates the complete audio transcription pipeline using Azure Speech Services,
coordinating between the fast transcription API, transcript processing, and output
generation components:

## Key Features:
----------------
- End-to-end transcription workflow management
- Integration with fast transcription API
- Real-time progress updates via callbacks
- Multiple output format generation
- Cost estimation based on duration
- Support for 30+ languages
- Comprehensive error handling

## Service Components:
---------------------
- FastTranscriptionService for Azure API integration
- TranscriptProcessor for result formatting
- TranscriptOutputGenerator for file creation
- Progress tracking throughout pipeline

"""

import os
from typing import Dict, Any, Optional, Callable, List
from datetime import datetime

from .fast_transcription_service import get_fast_transcription_service
from .transcript_processor import TranscriptProcessor
from .output_generator import TranscriptOutputGenerator
from utils.logging import get_logger, PerformanceTimer
from utils.exceptions import TranscriptionException

logger = get_logger(__name__)


class TranscriptionService:
    """Main service for audio transcription operations."""
    
    def __init__(self):
        """Initialize the service with sub-components."""
        self.fast_transcription = get_fast_transcription_service()
        self.processor = TranscriptProcessor()
        self.output_generator = TranscriptOutputGenerator()
    
    async def transcribe_audio(
        self,
        file_path: str,
        job_id: str,
        original_filename: str,
        language: str = "en-US",
        enable_diarization: bool = True,
        max_speakers: int = 20,
        progress_callback: Optional[Callable] = None
    ) -> Dict[str, Any]:
        """
        Transcribe audio file with comprehensive processing.
        
        Args:
            file_path: Path to audio file
            job_id: Job identifier
            original_filename: Original file name for output naming
            language: Language code
            enable_diarization: Enable speaker diarization
            max_speakers: Maximum speakers to identify
            progress_callback: Progress callback function
            
        Returns:
            Transcription results with download URL
        """
        with PerformanceTimer(logger, f"transcribe_audio_{job_id}"):
            try:
                # Step 1: Transcribe with Azure API
                if progress_callback:
                    await progress_callback(5, "Starting transcription process...")
                
                azure_result = await self.fast_transcription.transcribe_audio(
                    file_path=file_path,
                    job_id=job_id,
                    language=language,
                    enable_diarization=enable_diarization,
                    max_speakers=max_speakers,
                    progress_callback=progress_callback
                )
                
                # Step 2: Process transcription results
                if progress_callback:
                    await progress_callback(85, "Processing transcription results...")
                
                processed_data = self.processor.process_transcription_result(azure_result)
                
                # Step 3: Generate output files
                if progress_callback:
                    await progress_callback(90, "Creating output files...")
                
                results_path = await self.output_generator.create_results_package(
                    job_id=job_id,
                    processed_data=processed_data,
                    original_filename=original_filename
                )
                
                if progress_callback:
                    await progress_callback(100, "Transcription complete")
                
                # Prepare response
                result = {
                    'job_id': job_id,
                    'status': 'completed',
                    'results_path': results_path,
                    'statistics': processed_data['statistics'],
                    'speakers': len(processed_data['speakers']),
                    'duration': processed_data['duration_formatted'],
                    'language': language,
                    'diarization_enabled': enable_diarization
                }
                
                logger.info(
                    f"Transcription completed for job {job_id}: "
                    f"{processed_data['statistics']['total_words']} words, "
                    f"{len(processed_data['speakers'])} speakers"
                )
                
                return result
                
            except Exception as e:
                logger.error(f"Transcription failed for job {job_id}: {str(e)}")
                raise TranscriptionException(
                    message=f"Transcription failed: {str(e)}",
                    job_id=job_id,
                    details={'file_path': file_path}
                )
    
    async def estimate_cost(
        self,
        file_size_bytes: int,
        duration_seconds: float = 0
    ) -> Dict[str, Any]:
        """
        Estimate transcription cost.
        
        Args:
            file_size_bytes: File size in bytes
            duration_seconds: Duration in seconds (optional)
            
        Returns:
            Cost estimation details
        """
        file_size_mb = file_size_bytes / (1024 * 1024)
        return await self.fast_transcription.estimate_cost(
            duration_seconds=duration_seconds,
            file_size_mb=file_size_mb
        )
    
    def get_supported_formats(self) -> List[Dict[str, str]]:
        """Get list of supported audio formats."""
        return self.fast_transcription.get_supported_formats()
    
    def get_supported_languages(self) -> List[Dict[str, str]]:
        """Get list of supported languages for transcription."""
        # Common languages supported by Azure Speech Services
        return [
            {"code": "en-US", "name": "English (United States)"},
            {"code": "en-GB", "name": "English (United Kingdom)"},
            {"code": "en-AU", "name": "English (Australia)"},
            {"code": "en-CA", "name": "English (Canada)"},
            {"code": "es-ES", "name": "Spanish (Spain)"},
            {"code": "es-MX", "name": "Spanish (Mexico)"},
            {"code": "fr-FR", "name": "French (France)"},
            {"code": "fr-CA", "name": "French (Canada)"},
            {"code": "de-DE", "name": "German (Germany)"},
            {"code": "it-IT", "name": "Italian (Italy)"},
            {"code": "pt-BR", "name": "Portuguese (Brazil)"},
            {"code": "pt-PT", "name": "Portuguese (Portugal)"},
            {"code": "zh-CN", "name": "Chinese (Simplified)"},
            {"code": "zh-TW", "name": "Chinese (Traditional)"},
            {"code": "ja-JP", "name": "Japanese (Japan)"},
            {"code": "ko-KR", "name": "Korean (Korea)"},
            {"code": "ru-RU", "name": "Russian (Russia)"},
            {"code": "ar-SA", "name": "Arabic (Saudi Arabia)"},
            {"code": "hi-IN", "name": "Hindi (India)"},
            {"code": "nl-NL", "name": "Dutch (Netherlands)"},
            {"code": "sv-SE", "name": "Swedish (Sweden)"},
            {"code": "da-DK", "name": "Danish (Denmark)"},
            {"code": "fi-FI", "name": "Finnish (Finland)"},
            {"code": "nb-NO", "name": "Norwegian (Norway)"},
            {"code": "pl-PL", "name": "Polish (Poland)"},
            {"code": "tr-TR", "name": "Turkish (Turkey)"},
            {"code": "th-TH", "name": "Thai (Thailand)"},
            {"code": "cs-CZ", "name": "Czech (Czech Republic)"},
            {"code": "hu-HU", "name": "Hungarian (Hungary)"},
            {"code": "ro-RO", "name": "Romanian (Romania)"}
        ]


# Global service instance
_transcription_service: Optional[TranscriptionService] = None


def get_transcription_service() -> TranscriptionService:
    """Get global transcription service instance."""
    global _transcription_service
    if _transcription_service is None:
        _transcription_service = TranscriptionService()
    return _transcription_service