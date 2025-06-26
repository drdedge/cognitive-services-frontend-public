# backend/utils/validators.py
"""
Input validation utilities for the Azure Cognitive Services API.
"""
import mimetypes
import magic
from typing import List, Dict, Optional, Tuple
from pathlib import Path
import re
import hashlib
from .exceptions import ValidationException, FileSizeException, UnsupportedFileFormatException


# File type configurations
SUPPORTED_DOCUMENT_TYPES = {
    "application/pdf": [".pdf"],
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document": [".docx"],
    "application/msword": [".doc"],
    "text/plain": [".txt"],
    "application/rtf": [".rtf"],
    "image/jpeg": [".jpg", ".jpeg"],
    "image/png": [".png"],
    "image/tiff": [".tiff", ".tif"],
    "image/bmp": [".bmp"]
}

SUPPORTED_AUDIO_TYPES = {
    "audio/wav": [".wav"],
    "audio/mpeg": [".mp3"],
    "audio/mp4": [".m4a"],
    "audio/ogg": [".ogg"],
    "audio/flac": [".flac"],
    "audio/aiff": [".aiff", ".aif"],
    "audio/x-ms-wma": [".wma"]
}

SUPPORTED_IMAGE_TYPES = {
    "image/jpeg": [".jpg", ".jpeg"],
    "image/png": [".png"],
    "image/tiff": [".tiff", ".tif"],
    "image/bmp": [".bmp"],
    "image/gif": [".gif"],
    "image/webp": [".webp"]
}

# Language codes for translation
SUPPORTED_LANGUAGES = {
    "af", "ar", "bg", "bn", "ca", "cs", "cy", "da", "de", "el", "en", "es", "et", "fa", "fi", "fr",
    "ga", "gu", "he", "hi", "hr", "hu", "id", "is", "it", "ja", "ka", "kk", "ko", "lt", "lv", "ms",
    "mt", "nb", "nl", "pl", "pt", "ro", "ru", "sk", "sl", "sv", "sw", "ta", "te", "th", "tr", "uk",
    "ur", "vi", "zh"
}

# Speech recognition languages
SUPPORTED_SPEECH_LANGUAGES = {
    "en-US", "en-GB", "en-AU", "en-CA", "en-IN", "de-DE", "fr-FR", "es-ES", "it-IT", "pt-BR",
    "ja-JP", "ko-KR", "zh-CN", "zh-TW", "ar-EG", "hi-IN", "ru-RU", "nl-NL", "sv-SE", "da-DK",
    "fi-FI", "no-NO", "pl-PL", "pt-PT", "tr-TR", "th-TH", "vi-VN"
}


def validate_file_size(file_size: int, max_size: int) -> None:
    """
    Validate file size against maximum limit.
    
    Args:
        file_size: File size in bytes
        max_size: Maximum allowed size in bytes
        
    Raises:
        FileSizeException: If file exceeds maximum size
    """
    if file_size > max_size:
        raise FileSizeException(file_size, max_size)


def detect_file_type(file_path: str, file_content: bytes = None) -> Tuple[str, str]:
    """
    Detect file MIME type and extension.
    
    Args:
        file_path: Path to the file
        file_content: File content bytes (optional)
        
    Returns:
        Tuple of (mime_type, extension)
    """
    # Get extension from filename
    extension = Path(file_path).suffix.lower()
    
    # Try to detect MIME type from content if available
    if file_content:
        try:
            mime_type = magic.from_buffer(file_content, mime=True)
        except:
            # Fallback to mimetypes if python-magic fails
            mime_type, _ = mimetypes.guess_type(file_path)
    else:
        # Use mimetypes as fallback
        mime_type, _ = mimetypes.guess_type(file_path)
    
    # Normalize common MIME types
    if mime_type in ["application/x-pdf", "application/acrobat"]:
        mime_type = "application/pdf"
    elif mime_type in ["audio/x-wav", "audio/wave"]:
        mime_type = "audio/wav"
    elif mime_type in ["audio/mp3", "audio/mpeg3"]:
        mime_type = "audio/mpeg"
    
    return mime_type or "application/octet-stream", extension


def validate_file_type(file_path: str, file_content: bytes, service_type: str) -> str:
    """
    Validate file type for specific service.
    
    Args:
        file_path: Path to the file
        file_content: File content bytes
        service_type: Service type (document_intelligence, translation, transcription)
        
    Returns:
        Detected MIME type
        
    Raises:
        UnsupportedFileFormatException: If file type is not supported
    """
    mime_type, extension = detect_file_type(file_path, file_content)
    
    # Define supported types by service
    if service_type == "document_intelligence":
        supported_types = {**SUPPORTED_DOCUMENT_TYPES, **SUPPORTED_IMAGE_TYPES}
    elif service_type == "translation":
        supported_types = SUPPORTED_DOCUMENT_TYPES
    elif service_type == "transcription":
        supported_types = SUPPORTED_AUDIO_TYPES
    else:
        raise ValidationException(f"Unknown service type: {service_type}")
    
    # Check if MIME type is supported
    if mime_type not in supported_types:
        raise UnsupportedFileFormatException(
            detected_format=mime_type,
            supported_formats=list(supported_types.keys())
        )
    
    # Verify extension matches MIME type
    expected_extensions = supported_types[mime_type]
    if extension not in expected_extensions:
        raise UnsupportedFileFormatException(
            detected_format=f"{mime_type} with extension {extension}",
            supported_formats=[f"{mime_type} ({', '.join(exts)})" for mime_type, exts in supported_types.items()]
        )
    
    return mime_type


def validate_filename(filename: str) -> str:
    """
    Validate and sanitize filename.
    
    Args:
        filename: Original filename
        
    Returns:
        Sanitized filename
        
    Raises:
        ValidationException: If filename is invalid
    """
    if not filename:
        raise ValidationException("Filename cannot be empty")
    
    if len(filename) > 255:
        raise ValidationException("Filename too long (max 255 characters)")
    
    # Remove or replace invalid characters
    invalid_chars = r'[<>:"/\\|?*\x00-\x1f]'
    sanitized = re.sub(invalid_chars, '_', filename)
    
    # Remove leading/trailing dots and spaces
    sanitized = sanitized.strip('. ')
    
    if not sanitized:
        raise ValidationException("Invalid filename")
    
    return sanitized


def validate_language_code(language_code: str, service_type: str) -> str:
    """
    Validate language code for specific service.
    
    Args:
        language_code: Language code to validate
        service_type: Service type (translation, transcription)
        
    Returns:
        Validated language code
        
    Raises:
        ValidationException: If language code is invalid
    """
    if not language_code:
        raise ValidationException("Language code cannot be empty")
    
    language_code = language_code.lower().strip()
    
    if service_type == "translation":
        # Translation uses ISO 639-1 codes
        if language_code not in SUPPORTED_LANGUAGES:
            raise ValidationException(
                f"Unsupported language code: {language_code}",
                details={"supported_languages": sorted(SUPPORTED_LANGUAGES)}
            )
    elif service_type == "transcription":
        # Speech uses locale codes (e.g., en-US)
        if language_code not in SUPPORTED_SPEECH_LANGUAGES:
            raise ValidationException(
                f"Unsupported speech language: {language_code}",
                details={"supported_languages": sorted(SUPPORTED_SPEECH_LANGUAGES)}
            )
    else:
        raise ValidationException(f"Unknown service type: {service_type}")
    
    return language_code


def validate_job_id(job_id: str) -> str:
    """
    Validate job ID format.
    
    Args:
        job_id: Job ID to validate
        
    Returns:
        Validated job ID
        
    Raises:
        ValidationException: If job ID is invalid
    """
    if not job_id:
        raise ValidationException("Job ID cannot be empty")
    
    # Job ID should be alphanumeric with hyphens and underscores
    if not re.match(r'^[a-zA-Z0-9_-]+$', job_id):
        raise ValidationException("Job ID contains invalid characters")
    
    if len(job_id) < 3 or len(job_id) > 64:
        raise ValidationException("Job ID must be 3-64 characters long")
    
    return job_id


def calculate_file_hash(file_content: bytes, algorithm: str = "sha256") -> str:
    """
    Calculate hash of file content.
    
    Args:
        file_content: File content bytes
        algorithm: Hash algorithm (sha256, md5, sha1)
        
    Returns:
        Hex digest of file hash
    """
    if algorithm == "sha256":
        hasher = hashlib.sha256()
    elif algorithm == "md5":
        hasher = hashlib.md5()
    elif algorithm == "sha1":
        hasher = hashlib.sha1()
    else:
        raise ValidationException(f"Unsupported hash algorithm: {algorithm}")
    
    hasher.update(file_content)
    return hasher.hexdigest()


def validate_text_length(text: str, max_length: int = 50000, service_type: str = "translation") -> None:
    """
    Validate text length for processing.
    
    Args:
        text: Text to validate
        max_length: Maximum allowed length
        service_type: Service type for specific limits
        
    Raises:
        ValidationException: If text is too long
    """
    if not text:
        raise ValidationException("Text cannot be empty")
    
    if len(text) > max_length:
        raise ValidationException(
            f"Text too long: {len(text)} characters (max {max_length})",
            details={
                "text_length": len(text),
                "max_length": max_length,
                "service_type": service_type
            }
        )


def validate_cost_estimate_params(
    file_size: Optional[int] = None,
    page_count: Optional[int] = None,
    duration_minutes: Optional[float] = None,
    character_count: Optional[int] = None,
    service_type: str = None
) -> Dict:
    """
    Validate parameters for cost estimation.
    
    Args:
        file_size: File size in bytes
        page_count: Number of pages
        duration_minutes: Audio duration in minutes
        character_count: Number of characters for translation
        service_type: Service type
        
    Returns:
        Validated parameters dictionary
        
    Raises:
        ValidationException: If parameters are invalid
    """
    params = {}
    
    if service_type == "document_intelligence":
        if page_count is not None:
            if page_count <= 0 or page_count > 1000:
                raise ValidationException("Page count must be between 1 and 1000")
            params["page_count"] = page_count
        
        if file_size is not None:
            if file_size <= 0:
                raise ValidationException("File size must be positive")
            params["file_size"] = file_size
    
    elif service_type == "translation":
        if character_count is not None:
            if character_count <= 0 or character_count > 1000000:
                raise ValidationException("Character count must be between 1 and 1,000,000")
            params["character_count"] = character_count
    
    elif service_type == "transcription":
        if duration_minutes is not None:
            if duration_minutes <= 0 or duration_minutes > 1440:  # 24 hours
                raise ValidationException("Duration must be between 1 minute and 24 hours")
            params["duration_minutes"] = duration_minutes
    
    else:
        raise ValidationException(f"Unknown service type: {service_type}")
    
    return params


def sanitize_metadata(metadata: Dict[str, str]) -> Dict[str, str]:
    """
    Sanitize metadata for storage.
    
    Args:
        metadata: Metadata dictionary
        
    Returns:
        Sanitized metadata
    """
    sanitized = {}
    
    for key, value in metadata.items():
        # Sanitize key
        clean_key = re.sub(r'[^a-zA-Z0-9_-]', '_', str(key))[:64]
        
        # Sanitize value
        clean_value = str(value)[:1024]  # Limit length
        clean_value = re.sub(r'[\x00-\x1f\x7f-\x9f]', '', clean_value)  # Remove control chars
        
        if clean_key and clean_value:
            sanitized[clean_key] = clean_value
    
    return sanitized