# backend/services/shared/__init__.py
"""
Shared Service Utilities
========================

Common utilities and processors used across all Azure Cognitive Services
to reduce code duplication and ensure consistency.
"""

from .file_processor import FileProcessor
from .result_packager import ResultPackager

__all__ = ['FileProcessor', 'ResultPackager']