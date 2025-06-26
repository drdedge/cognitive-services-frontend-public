"""
Sample data and fixtures for testing various scenarios.
"""
from datetime import datetime, timedelta
import json


# Sample document intelligence results
SAMPLE_DOCUMENT_ANALYSIS = {
    "job_id": "doc-analysis-123",
    "status": "completed",
    "confidence": 0.92,
    "pages": [
        {
            "page_number": 1,
            "width": 8.5,
            "height": 11.0,
            "text": "Sample document content with tables and formatted text.",
            "words": [
                {"content": "Sample", "confidence": 0.95, "bounding_box": [1.0, 1.0, 2.0, 1.5]},
                {"content": "document", "confidence": 0.93, "bounding_box": [2.1, 1.0, 3.2, 1.5]},
                {"content": "content", "confidence": 0.97, "bounding_box": [3.3, 1.0, 4.1, 1.5]}
            ]
        }
    ],
    "tables": [
        {
            "table_id": 1,
            "row_count": 3,
            "column_count": 2,
            "cells": [
                {"content": "Header 1", "row_index": 0, "column_index": 0, "confidence": 0.98},
                {"content": "Header 2", "row_index": 0, "column_index": 1, "confidence": 0.96},
                {"content": "Data 1", "row_index": 1, "column_index": 0, "confidence": 0.94},
                {"content": "Data 2", "row_index": 1, "column_index": 1, "confidence": 0.92},
                {"content": "Data 3", "row_index": 2, "column_index": 0, "confidence": 0.89},
                {"content": "Data 4", "row_index": 2, "column_index": 1, "confidence": 0.91}
            ]
        }
    ],
    "processing_time": 45.2,
    "cost": 2.50
}

# Sample translation results
SAMPLE_TRANSLATION_RESULT = {
    "job_id": "translation-456",
    "source_language": "en",
    "target_language": "es",
    "detected_language": {
        "language": "en",
        "confidence": 0.99
    },
    "translations": [
        {
            "original_text": "Hello world! This is a test document.",
            "translated_text": "¡Hola mundo! Este es un documento de prueba.",
            "confidence": 0.95
        },
        {
            "original_text": "Please review the attached table.",
            "translated_text": "Por favor revise la tabla adjunta.",
            "confidence": 0.93
        }
    ],
    "character_count": 65,
    "processing_time": 12.8,
    "cost": 0.75
}

# Sample transcription results
SAMPLE_TRANSCRIPTION_RESULT = {
    "job_id": "transcription-789",
    "language": "en-US",
    "status": "completed",
    "duration_seconds": 180.5,
    "transcript": "Hello, this is a sample audio transcription. The speaker is discussing various topics related to artificial intelligence and machine learning.",
    "confidence": 0.89,
    "word_timestamps": [
        {"word": "Hello", "start": 0.0, "end": 0.5, "confidence": 0.95},
        {"word": "this", "start": 0.6, "end": 0.8, "confidence": 0.92},
        {"word": "is", "start": 0.9, "end": 1.0, "confidence": 0.94},
        {"word": "a", "start": 1.1, "end": 1.2, "confidence": 0.88},
        {"word": "sample", "start": 1.3, "end": 1.8, "confidence": 0.91}
    ],
    "speaker_diarization": [
        {"speaker": "Speaker_1", "start": 0.0, "end": 30.5},
        {"speaker": "Speaker_2", "start": 30.6, "end": 60.2},
        {"speaker": "Speaker_1", "start": 60.3, "end": 180.5}
    ],
    "processing_time": 25.1,
    "cost": 3.00
}

# Sample job status progression
SAMPLE_JOB_STATUSES = [
    {
        "status": "pending",
        "progress": 0,
        "message": "Job queued for processing",
        "timestamp": "2024-01-14T10:00:00Z"
    },
    {
        "status": "processing",
        "progress": 10,
        "message": "Starting document analysis",
        "timestamp": "2024-01-14T10:00:30Z"
    },
    {
        "status": "processing",
        "progress": 25,
        "message": "Analyzing page 1 of 4",
        "timestamp": "2024-01-14T10:01:15Z"
    },
    {
        "status": "processing",
        "progress": 50,
        "message": "Analyzing page 2 of 4",
        "timestamp": "2024-01-14T10:02:00Z"
    },
    {
        "status": "processing",
        "progress": 75,
        "message": "Extracting tables and formatting results",
        "timestamp": "2024-01-14T10:02:45Z"
    },
    {
        "status": "processing",
        "progress": 90,
        "message": "Packaging results",
        "timestamp": "2024-01-14T10:03:20Z"
    },
    {
        "status": "completed",
        "progress": 100,
        "message": "Processing completed successfully",
        "timestamp": "2024-01-14T10:03:45Z"
    }
]

# Sample error scenarios
SAMPLE_ERROR_SCENARIOS = {
    "file_too_large": {
        "error_code": "FILE_SIZE_EXCEEDED",
        "error_message": "File size exceeds maximum limit of 50MB",
        "details": {
            "file_size": 52428800,  # 50MB
            "max_size": 52428800,   # 50MB
            "suggested_action": "Please reduce file size or split into smaller files"
        }
    },
    "unsupported_format": {
        "error_code": "UNSUPPORTED_FILE_FORMAT",
        "error_message": "File format not supported for this service",
        "details": {
            "detected_format": "image/jpeg",
            "supported_formats": ["application/pdf", "application/vnd.openxmlformats-officedocument.wordprocessingml.document"],
            "suggested_action": "Please convert file to a supported format"
        }
    },
    "azure_service_error": {
        "error_code": "AZURE_SERVICE_UNAVAILABLE",
        "error_message": "Azure Cognitive Services temporarily unavailable",
        "details": {
            "service": "document-intelligence",
            "error_type": "temporary",
            "retry_after": 300,
            "suggested_action": "Please try again in a few minutes"
        }
    },
    "authentication_error": {
        "error_code": "AUTHENTICATION_FAILED",
        "error_message": "Invalid API credentials",
        "details": {
            "service": "translator",
            "error_type": "configuration",
            "suggested_action": "Please check API key configuration"
        }
    }
}

# Sample cost calculations
SAMPLE_COST_ESTIMATES = {
    "document_intelligence": {
        "per_page": 0.01,
        "table_extraction": 0.005,
        "ocr_premium": 0.002,
        "examples": [
            {"pages": 1, "tables": 0, "cost": 0.01},
            {"pages": 5, "tables": 2, "cost": 0.06},
            {"pages": 10, "tables": 5, "cost": 0.125}
        ]
    },
    "translation": {
        "per_million_chars": 15.00,
        "document_premium": 1.5,  # Multiplier for document translation
        "examples": [
            {"chars": 1000, "languages": 1, "cost": 0.015},
            {"chars": 10000, "languages": 2, "cost": 0.30},
            {"chars": 50000, "languages": 1, "is_document": True, "cost": 1.125}
        ]
    },
    "transcription": {
        "per_minute": 1.00,
        "diarization_premium": 0.50,
        "examples": [
            {"minutes": 5, "diarization": False, "cost": 5.00},
            {"minutes": 30, "diarization": True, "cost": 45.00},
            {"minutes": 120, "diarization": False, "cost": 120.00}
        ]
    }
}

# Sample WebSocket messages
SAMPLE_WEBSOCKET_MESSAGES = {
    "job_update": {
        "type": "job_update",
        "job_id": "test-job-123",
        "status": "processing",
        "progress": 45,
        "message": "Processing page 3 of 7",
        "timestamp": "2024-01-14T10:02:15Z"
    },
    "error": {
        "type": "error",
        "job_id": "test-job-123",
        "error_code": "PROCESSING_ERROR",
        "error_message": "Failed to extract tables from page 4",
        "retry_possible": True,
        "timestamp": "2024-01-14T10:02:30Z"
    },
    "completion": {
        "type": "job_completed",
        "job_id": "test-job-123",
        "status": "completed",
        "results_url": "https://storage.blob.core.windows.net/results/test-job-123-output.zip",
        "final_cost": 2.75,
        "processing_time": 125.3,
        "timestamp": "2024-01-14T10:04:20Z"
    },
    "cost_estimate": {
        "type": "cost_estimate",
        "job_id": "test-job-123",
        "estimated_cost": 2.50,
        "breakdown": {
            "document_processing": 1.50,
            "table_extraction": 0.75,
            "ocr": 0.25
        },
        "confidence": "high",
        "timestamp": "2024-01-14T10:00:45Z"
    }
}

# Sample file metadata
SAMPLE_FILE_METADATA = {
    "pdf": {
        "filename": "sample_document.pdf",
        "size_bytes": 2048576,  # 2MB
        "mime_type": "application/pdf",
        "pdf_version": "1.4",
        "page_count": 10,
        "author": "Test User",
        "title": "Sample Document",
        "created": "2024-01-10T09:00:00Z",
        "modified": "2024-01-12T14:30:00Z",
        "encrypted": False,
        "has_forms": False,
        "has_signatures": False
    },
    "docx": {
        "filename": "sample_document.docx",
        "size_bytes": 1524800,  # 1.5MB
        "mime_type": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        "page_count": 8,
        "word_count": 2500,
        "character_count": 15000,
        "author": "Test User",
        "title": "Sample DOCX Document",
        "created": "2024-01-11T11:00:00Z",
        "modified": "2024-01-13T16:45:00Z",
        "has_tables": True,
        "has_images": False,
        "has_macros": False
    },
    "audio": {
        "filename": "sample_audio.wav",
        "size_bytes": 10485760,  # 10MB
        "mime_type": "audio/wav",
        "duration_seconds": 300.5,
        "sample_rate": 44100,
        "channels": 2,
        "bit_depth": 16,
        "bitrate": 1411,
        "format": "PCM",
        "created": "2024-01-12T08:30:00Z"
    }
}

# Sample Azure service responses
SAMPLE_AZURE_RESPONSES = {
    "document_intelligence_success": {
        "status": "succeeded",
        "created_datetime": "2024-01-14T10:00:00Z",
        "last_updated_datetime": "2024-01-14T10:03:45Z",
        "analyze_result": {
            "api_version": "2023-07-31",
            "model_id": "prebuilt-document",
            "content": "Sample document content...",
            "pages": [],
            "tables": [],
            "styles": [],
            "paragraphs": []
        }
    },
    "translator_success": {
        "translations": [
            {
                "text": "Translated text content",
                "to": "es"
            }
        ],
        "detectedLanguage": {
            "language": "en",
            "score": 0.99
        }
    },
    "speech_service_success": {
        "RecognitionStatus": "Success",
        "DisplayText": "Transcribed speech content.",
        "Offset": 0,
        "Duration": 18050000,
        "NBest": [
            {
                "Confidence": 0.89,
                "Lexical": "transcribed speech content",
                "ITN": "transcribed speech content",
                "MaskedITN": "transcribed speech content",
                "Display": "Transcribed speech content."
            }
        ]
    }
}

# Test data for different file sizes
FILE_SIZE_TEST_DATA = {
    "small": {
        "size_bytes": 1024,  # 1KB
        "expected_processing_time": 1.0,
        "expected_cost": 0.01
    },
    "medium": {
        "size_bytes": 1048576,  # 1MB
        "expected_processing_time": 10.0,
        "expected_cost": 0.50
    },
    "large": {
        "size_bytes": 52428800,  # 50MB
        "expected_processing_time": 120.0,
        "expected_cost": 5.00
    },
    "oversized": {
        "size_bytes": 104857600,  # 100MB
        "should_reject": True,
        "error_code": "FILE_SIZE_EXCEEDED"
    }
}

# Performance benchmarks
PERFORMANCE_BENCHMARKS = {
    "document_intelligence": {
        "max_processing_time_per_page": 30.0,  # seconds
        "max_memory_usage_mb": 200,
        "target_accuracy": 0.90
    },
    "translation": {
        "max_processing_time_per_1k_chars": 2.0,  # seconds
        "max_memory_usage_mb": 100,
        "target_accuracy": 0.95
    },
    "transcription": {
        "max_processing_time_per_minute": 10.0,  # seconds (10x real-time)
        "max_memory_usage_mb": 150,
        "target_accuracy": 0.85
    }
}


def get_sample_data(data_type: str, scenario: str = "default"):
    """
    Get sample test data by type and scenario.
    
    Args:
        data_type: Type of data (e.g., 'document_analysis', 'translation', etc.)
        scenario: Specific scenario (e.g., 'success', 'error', 'large_file', etc.)
    
    Returns:
        Dictionary containing sample data
    """
    data_map = {
        "document_analysis": SAMPLE_DOCUMENT_ANALYSIS,
        "translation": SAMPLE_TRANSLATION_RESULT,
        "transcription": SAMPLE_TRANSCRIPTION_RESULT,
        "job_statuses": SAMPLE_JOB_STATUSES,
        "errors": SAMPLE_ERROR_SCENARIOS,
        "costs": SAMPLE_COST_ESTIMATES,
        "websocket": SAMPLE_WEBSOCKET_MESSAGES,
        "metadata": SAMPLE_FILE_METADATA,
        "azure_responses": SAMPLE_AZURE_RESPONSES,
        "file_sizes": FILE_SIZE_TEST_DATA,
        "benchmarks": PERFORMANCE_BENCHMARKS
    }
    
    data = data_map.get(data_type, {})
    
    if scenario != "default" and isinstance(data, dict):
        return data.get(scenario, data)
    
    return data