# backend/services/base/__init__.py
"""
Base Service Classes
====================

Provides abstract base classes and common functionality for all Azure Cognitive
Services implementations to ensure consistency and reduce code duplication.
"""

from .base_service import BaseAzureService, ProcessingResult
from .result_packager import ResultPackager

__all__ = ['BaseAzureService', 'ProcessingResult', 'ResultPackager']