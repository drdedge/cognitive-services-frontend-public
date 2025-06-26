# backend/services/document_intelligence/__init__.py
"""
Document Intelligence service package with Azure Form Recognizer integration
===========================================================================

This package provides a comprehensive service for extracting text, tables, and 
structural information from documents using Azure's Document Intelligence API:

## Key Features:
-----------------
- Multi-format document analysis (PDF, images, Office documents)
- Table extraction with confidence scoring
- Text extraction with markdown formatting
- Layout analysis with bounding boxes
- Confidence dashboard generation
- Real-time progress updates via WebSocket

The service handles the complete document processing pipeline from file upload
through Azure API interaction to result packaging and delivery.
"""

from .service import DocumentIntelligenceService, get_document_intelligence_service
from .result_packager import DocumentIntelligenceResultPackager

__all__ = ['DocumentIntelligenceService', 'get_document_intelligence_service', 'DocumentIntelligenceResultPackager']