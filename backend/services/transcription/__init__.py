#backend/services/transcription/__init__.py
"""
Transcription service module with Azure Speech Services
======================================================

Provides comprehensive audio transcription capabilities using Azure Speech Services
fast transcription API, featuring speaker diarization, multiple output formats, and
real-time progress tracking:

## Key Features:
----------------
- Fast transcription API for audio files up to 2 hours
- Speaker diarization with up to 20 speakers
- Multiple output formats (TXT, JSON, SRT, VTT)
- 1-minute chunked transcripts for easy navigation
- Comprehensive speaker analysis and statistics
- Support for 11 audio formats (WAV, MP3, OPUS, etc)
- Real-time progress updates via WebSocket

## Performance Optimizations:
-----------------------------
- Asynchronous processing with progress callbacks
- Efficient file streaming for large audio files
- Automatic cleanup of temporary files
- Modular architecture for easy maintenance

"""

from .service import TranscriptionService, get_transcription_service
from .fast_transcription_service import FastTranscriptionService
from .transcript_processor import TranscriptProcessor
from .output_generator import TranscriptOutputGenerator
from .result_packager import TranscriptionResultPackager

__all__ = [
    'TranscriptionService',
    'get_transcription_service',
    'FastTranscriptionService',
    'TranscriptProcessor', 
    'TranscriptOutputGenerator',
    'TranscriptionResultPackager'
]