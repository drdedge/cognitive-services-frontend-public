# backend/models/translation_models.py
"""
Translation data models
=======================
"""

from typing import List, Dict, Optional
from pydantic import BaseModel, Field


class TranslationRequest(BaseModel):
    """Request model for text translation."""
    text: str = Field(..., min_length=1, max_length=50000)
    target_languages: List[str] = Field(..., min_items=1)
    source_language: Optional[str] = None
    text_type: str = Field(default="plain", pattern="^(plain|html)$")


class TranslationItem(BaseModel):
    """Individual translation result."""
    language: str
    text: str
    confidence: Optional[float] = None


class TranslationResponse(BaseModel):
    """Response model for translation."""
    original_text: str
    detected_language: Optional[str] = None
    translations: List[Dict[str, str]]  # Changed from List[TranslationItem] to match service output


class LanguageDetectionResponse(BaseModel):
    """Response model for language detection."""
    language: str
    confidence: float
    is_translation_supported: bool
    is_transliteration_supported: bool


class SupportedLanguage(BaseModel):
    """Supported language model."""
    code: str
    name: str
    native_name: str
    direction: str = Field(default="ltr", pattern="^(ltr|rtl)$")


class SupportedLanguagesResponse(BaseModel):
    """Response model for supported languages."""
    languages: List[SupportedLanguage]
    total: int = Field(default=0)


class DocumentTranslationRequest(BaseModel):
    """Request model for document translation."""
    source_language: Optional[str] = None
    target_language: str
    preserve_formatting: bool = True


class DocumentTranslationResponse(BaseModel):
    """Response model for document translation."""
    task_id: str
    status: str
    source_language: Optional[str] = None
    target_language: str
    translated_file_url: Optional[str] = None
    progress: int = Field(default=0, ge=0, le=100)