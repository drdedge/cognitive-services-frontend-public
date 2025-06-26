# backend/models/transcription_models.py
"""
Transcription data models
=========================
"""

from enum import Enum
from typing import List, Dict, Optional, Any
from datetime import datetime
from pydantic import BaseModel, Field
from fastapi import Form


class TranscriptionStatus(str, Enum):
    """Transcription status enumeration."""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


# New class added to handle API endpoint options
class TranscriptionOptions(BaseModel):
    """
    Defines and validates the options for a transcription request.
    FastAPI uses this model to parse and validate form data from the request.
    """
    language: str = Form(default="en-US", description="Language code for transcription.")
    enable_diarization: bool = Form(default=True, description="Enable speaker diarization.")
    max_speakers: int = Form(default=20, description="Maximum number of speakers to identify.")


class TranscriptionRequest(BaseModel):
    """Request model for audio transcription."""
    language: str = Field(default="en-US")
    enable_diarization: bool = False
    enable_punctuation: bool = True
    output_format: str = Field(default="text", pattern="^(text|srt|vtt|json)$")
    profanity_filter: bool = True


class TranscriptionSegment(BaseModel):
    """Transcription segment model."""
    start_time: float
    end_time: float
    text: str
    speaker: Optional[str] = None
    confidence: Optional[float] = None


class TranscriptionResponse(BaseModel):
    """Response model for transcription."""
    task_id: str
    status: TranscriptionStatus
    message: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = None
    language: Optional[str] = None
    duration_seconds: Optional[float] = None
    transcription: Optional[str] = None
    segments: Optional[List[TranscriptionSegment]] = None
    word_count: Optional[int] = None
    error: Optional[str] = None

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat() if v else None
        }


class RealtimeTranscriptionConfig(BaseModel):
    """Configuration for real-time transcription."""
    language: str = Field(default="en-US")
    enable_interim_results: bool = True
    enable_punctuation: bool = True
    profanity_filter: bool = True
    session_id: str


class RealtimeTranscriptionUpdate(BaseModel):
    """Real-time transcription update."""
    session_id: str
    segment_id: int
    is_final: bool
    text: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    speaker: Optional[str] = None

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat() if v else None
        }