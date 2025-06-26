"""
Translation result packager implementation.

Handles packaging of translation results for both text and document translations,
including language detection and metadata.
"""
import os
import json
from typing import Dict, Any, List, Optional
from pathlib import Path

from services.shared.result_packager import ResultPackager
from utils.logging import get_logger

logger = get_logger(__name__)


class TranslationResultPackager(ResultPackager):
    """
    Result packager for Translation service.
    
    Packages:
    - Original and translated content (text or documents)
    - Language detection results
    - Translation metadata and statistics
    - Comprehensive translation reports
    """
    
    @property
    def service_name(self) -> str:
        """Get the service name."""
        return "translation"
    
    async def _package_service_results(
        self, 
        temp_dir: str,
        results: Dict[str, Any],
        original_filename: str,
        metadata: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Package Translation specific results.
        
        Args:
            temp_dir: Temporary directory for packaging
            results: Processing results containing translations
            original_filename: Original filename (document or text identifier)
            metadata: Additional metadata including translation options
            
        Returns:
            Dictionary with packaging statistics
        """
        files = []
        stats = {
            "translation_type": results.get("type", "text"),
            "source_language": results.get("source_language", "auto-detect"),
            "target_language": results.get("target_language", "unknown"),
            "characters_translated": results.get("characters_count", 0),
            "confidence_score": results.get("confidence", 1.0),
            "processing_time": metadata.get("processing_time", 0)
        }
        
        # Handle document translation
        if stats["translation_type"] == "document":
            # Save original document if available
            if "original_file_path" in results and os.path.exists(results["original_file_path"]):
                dest_path = os.path.join(temp_dir, "original", original_filename)
                file_info = await self._copy_file(
                    results["original_file_path"], 
                    dest_path,
                    "Original document"
                )
                files.append(file_info)
            
            # Save translated document
            if "translated_file_path" in results and os.path.exists(results["translated_file_path"]):
                base_name = Path(original_filename).stem
                ext = Path(original_filename).suffix
                translated_name = f"{base_name}_{results.get('target_language', 'translated')}{ext}"
                dest_path = os.path.join(temp_dir, "processed", translated_name)
                
                file_info = await self._copy_file(
                    results["translated_file_path"],
                    dest_path,
                    f"Translated document ({results.get('target_language', 'unknown')})"
                )
                files.append(file_info)
                stats["translated_file_size"] = file_info["size"]
            
            # Save extracted text if available
            if "original_text" in results:
                text_path = os.path.join(
                    temp_dir,
                    "metadata",
                    f"{Path(original_filename).stem}_original_text.txt"
                )
                file_info = await self._save_text_file(
                    results["original_text"],
                    text_path,
                    "Extracted original text"
                )
                files.append(file_info)
            
            if "translated_text" in results:
                text_path = os.path.join(
                    temp_dir,
                    "metadata",
                    f"{Path(original_filename).stem}_translated_text.txt"
                )
                file_info = await self._save_text_file(
                    results["translated_text"],
                    text_path,
                    f"Translated text ({results.get('target_language', 'unknown')})"
                )
                files.append(file_info)
        
        # Handle text translation
        else:
            # Save original text
            if "original_text" in results:
                original_path = os.path.join(
                    temp_dir,
                    "original",
                    "original_text.txt"
                )
                file_info = await self._save_text_file(
                    results["original_text"],
                    original_path,
                    "Original text"
                )
                files.append(file_info)
            
            # Save translated text
            if "translated_text" in results:
                translated_path = os.path.join(
                    temp_dir,
                    "processed",
                    f"translated_text_{results.get('target_language', 'unknown')}.txt"
                )
                file_info = await self._save_text_file(
                    results["translated_text"],
                    translated_path,
                    f"Translated text ({results.get('target_language', 'unknown')})"
                )
                files.append(file_info)
        
        # Save language detection results
        if "language_detection" in results:
            detection_path = os.path.join(
                temp_dir,
                "metadata",
                "language_detection.json"
            )
            file_info = await self._save_json_file(
                results["language_detection"],
                detection_path,
                "Language detection results"
            )
            files.append(file_info)
        
        # Create translation report
        translation_report = self._create_translation_report(results, stats, metadata)
        report_path = os.path.join(temp_dir, "reports", "translation_report.json")
        file_info = await self._save_json_file(
            translation_report,
            report_path,
            "Comprehensive translation report"
        )
        files.append(file_info)
        
        # Save translation summary
        summary_text = self._create_summary_text(results, stats, metadata)
        summary_path = os.path.join(temp_dir, "reports", "translation_summary.txt")
        file_info = await self._save_text_file(
            summary_text,
            summary_path,
            "Translation summary"
        )
        files.append(file_info)
        
        # Save raw Azure response if available
        if "azure_response" in results:
            response_path = os.path.join(temp_dir, "metadata", "azure_translator_response.json")
            file_info = await self._save_json_file(
                results["azure_response"],
                response_path,
                "Raw Azure Translator response"
            )
            files.append(file_info)
        
        # Save translation alternatives if available
        if "alternatives" in results:
            alt_path = os.path.join(temp_dir, "metadata", "translation_alternatives.json")
            file_info = await self._save_json_file(
                results["alternatives"],
                alt_path,
                "Alternative translations"
            )
            files.append(file_info)
        
        stats["files_count"] = len(files)
        stats["files"] = files
        
        return stats
    
    def _create_translation_report(
        self, 
        results: Dict[str, Any], 
        stats: Dict[str, Any],
        metadata: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Create a comprehensive translation report.
        
        Args:
            results: Processing results
            stats: Processing statistics
            metadata: Translation metadata
            
        Returns:
            Translation report dictionary
        """
        report = {
            "translation_summary": {
                "type": stats["translation_type"],
                "source_language": stats["source_language"],
                "target_language": stats["target_language"],
                "detected_language": results.get("detected_language", stats["source_language"]),
                "characters_translated": stats["characters_translated"],
                "words_translated": results.get("words_count", 0),
                "confidence_score": round(stats["confidence_score"], 3),
                "processing_time_seconds": round(stats["processing_time"], 2)
            },
            "translation_details": {
                "translation_model": results.get("model", "standard"),
                "formality": metadata.get("formality", "default"),
                "profanity_action": metadata.get("profanity_action", "no_action"),
                "preserve_formatting": metadata.get("preserve_formatting", True)
            }
        }
        
        # Add language detection details if available
        if "language_detection" in results:
            detection = results["language_detection"]
            report["language_detection"] = {
                "detected_language": detection.get("language", "unknown"),
                "confidence": round(detection.get("confidence", 0), 3),
                "alternatives": detection.get("alternatives", [])
            }
        
        # Add document-specific details
        if stats["translation_type"] == "document":
            report["document_details"] = {
                "original_format": results.get("document_format", "unknown"),
                "pages_count": results.get("pages_count", 0),
                "tables_preserved": results.get("tables_preserved", False),
                "formatting_preserved": results.get("formatting_preserved", True)
            }
        
        # Add quality metrics if available
        if "quality_metrics" in results:
            report["quality_metrics"] = results["quality_metrics"]
        
        # Add warnings or notes
        if "warnings" in results:
            report["warnings"] = results["warnings"]
        
        return report
    
    def _create_summary_text(
        self, 
        results: Dict[str, Any], 
        stats: Dict[str, Any],
        metadata: Dict[str, Any]
    ) -> str:
        """
        Create a human-readable summary text.
        
        Args:
            results: Processing results
            stats: Processing statistics
            metadata: Translation metadata
            
        Returns:
            Summary text string
        """
        lines = [
            "TRANSLATION SUMMARY",
            "=" * 50,
            "",
            f"Translation Type: {stats['translation_type'].capitalize()}",
            f"Source Language: {self._format_language(stats['source_language'])}",
            f"Target Language: {self._format_language(stats['target_language'])}",
        ]
        
        if results.get("detected_language") and stats["source_language"] == "auto-detect":
            lines.append(f"Detected Language: {self._format_language(results['detected_language'])}")
        
        lines.extend([
            "",
            "STATISTICS",
            "-" * 20,
            f"Characters Translated: {stats['characters_translated']:,}",
        ])
        
        if "words_count" in results:
            lines.append(f"Words Translated: {results['words_count']:,}")
        
        if stats["translation_type"] == "document" and "pages_count" in results:
            lines.append(f"Pages Processed: {results['pages_count']}")
        
        lines.extend([
            f"Processing Time: {round(stats['processing_time'], 2)} seconds",
            "",
            "CONFIGURATION",
            "-" * 20,
            f"Translation Model: {results.get('model', 'standard')}",
        ])
        
        if "formality" in metadata and metadata["formality"] != "default":
            lines.append(f"Formality: {metadata['formality']}")
        
        if "profanity_action" in metadata and metadata["profanity_action"] != "no_action":
            lines.append(f"Profanity Action: {metadata['profanity_action']}")
        
        lines.extend([
            "",
            f"Generated at: {metadata.get('timestamp', 'Unknown')}",
            f"Job ID: {metadata.get('job_id', 'Unknown')}"
        ])
        
        return "\n".join(lines)
    
    def _format_language(self, lang_code: str) -> str:
        """
        Format language code to readable format.
        
        Args:
            lang_code: Language code (e.g., 'en', 'es', 'fr')
            
        Returns:
            Formatted language string
        """
        # This could be expanded with a full language mapping
        language_map = {
            "en": "English",
            "es": "Spanish",
            "fr": "French",
            "de": "German",
            "it": "Italian",
            "pt": "Portuguese",
            "zh": "Chinese",
            "ja": "Japanese",
            "ko": "Korean",
            "ar": "Arabic",
            "auto-detect": "Auto-Detect"
        }
        
        return language_map.get(lang_code, lang_code.upper())