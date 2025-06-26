"""
Tests for service-specific ResultPackager implementations.

Tests the Document Intelligence, Transcription, and Translation packagers
to ensure they correctly package their respective results.
"""
import os
import json
import tempfile
from unittest.mock import Mock, AsyncMock, patch
import pytest

from services.document_intelligence.result_packager import DocumentIntelligenceResultPackager
from services.transcription.result_packager import TranscriptionResultPackager
from services.translation.result_packager import TranslationResultPackager
from utils.file_handler import FileHandler


class TestDocumentIntelligenceResultPackager:
    """Test suite for Document Intelligence ResultPackager."""
    
    @pytest.fixture
    def mock_file_handler(self):
        """Create mock FileHandler."""
        handler = Mock(spec=FileHandler)
        handler.upload_to_blob = AsyncMock(return_value="https://test.blob.core.windows.net/test.zip")
        return handler
    
    @pytest.fixture
    def packager(self, mock_file_handler):
        """Create Document Intelligence packager instance."""
        return DocumentIntelligenceResultPackager(mock_file_handler)
    
    @pytest.fixture
    def sample_results(self):
        """Create sample Document Intelligence results."""
        return {
            "markdown_content": "# Document Title\n\nThis is the document content.",
            "page_markdowns": [
                "# Page 1\nFirst page content",
                "# Page 2\nSecond page content"
            ],
            "pages_count": 2,
            "tables_count": 1,
            "average_confidence": 0.95,
            "total_characters": 1500,
            "total_words": 250,
            "total_lines": 30,
            "model_used": "prebuilt-layout",
            "table_details": [
                {
                    "page": 1,
                    "rows": 3,
                    "columns": 4,
                    "cells": 12,
                    "confidence": 0.98
                }
            ],
            "confidence_stats": {
                "min": 0.85,
                "max": 0.99,
                "mean": 0.95
            }
        }
    
    @pytest.mark.asyncio
    async def test_package_document_intelligence_results(self, packager, sample_results):
        """Test packaging of Document Intelligence results."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create standard directory structure first
            packager._create_standard_structure(temp_dir)
            
            metadata = {"processing_time": 5.3}
            
            stats = await packager._package_service_results(
                temp_dir, sample_results, "test_doc.pdf", metadata
            )
            
            # Check statistics
            assert stats["pages_count"] == 2
            assert stats["tables_count"] == 1
            assert stats["confidence_score"] == 0.95
            assert stats["processing_time"] == 5.3
            assert stats["files_count"] > 0
            
            # Check markdown file was created
            md_path = os.path.join(temp_dir, "processed", "test_doc_document.md")
            assert os.path.exists(md_path)
            with open(md_path, 'r') as f:
                content = f.read()
            assert content == sample_results["markdown_content"]
            
            # Check page markdown files
            page1_path = os.path.join(temp_dir, "processed", "pages", "test_doc_page1.md")
            assert os.path.exists(page1_path)
            
            # Check analysis summary
            summary_path = os.path.join(temp_dir, "reports", "analysis_summary.json")
            assert os.path.exists(summary_path)
            with open(summary_path, 'r') as f:
                summary = json.load(f)
            assert summary["document_analysis"]["pages_analyzed"] == 2
            assert summary["document_analysis"]["average_confidence"] == 0.95
    
    @pytest.mark.asyncio
    async def test_package_with_tables_and_excel(self, packager):
        """Test packaging with table extraction results."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create standard directory structure first
            packager._create_standard_structure(temp_dir)
            
            # Create mock CSV and Excel files
            csv_path = os.path.join(temp_dir, "table1.csv")
            with open(csv_path, 'w') as f:
                f.write("col1,col2\nval1,val2\n")
            
            excel_path = os.path.join(temp_dir, "tables.xlsx")
            with open(excel_path, 'wb') as f:
                f.write(b"mock excel content")
            
            results = {
                "pages_count": 1,
                "tables_count": 1,
                "table_csv_files": [
                    {"path": csv_path, "filename": "table1.csv", "page": 1}
                ],
                "excel_file_path": excel_path
            }
            
            stats = await packager._package_service_results(
                temp_dir, results, "doc.pdf", {}
            )
            
            # Check CSV was copied
            dest_csv = os.path.join(temp_dir, "processed", "tables", "csv", "table1.csv")
            assert os.path.exists(dest_csv)
            
            # Check Excel was copied
            dest_excel = os.path.join(temp_dir, "processed", "doc_tables.xlsx")
            assert os.path.exists(dest_excel)
            assert "excel_file_size" in stats
    
    @pytest.mark.asyncio
    async def test_package_with_confidence_dashboard(self, packager):
        """Test packaging with confidence dashboard."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create standard directory structure first
            packager._create_standard_structure(temp_dir)
            
            # Create mock dashboard image
            dashboard_path = os.path.join(temp_dir, "dashboard.png")
            with open(dashboard_path, 'wb') as f:
                f.write(b"PNG mock image content")
            
            results = {
                "pages_count": 1,
                "confidence_dashboard_path": dashboard_path
            }
            
            await packager._package_service_results(
                temp_dir, results, "doc.pdf", {}
            )
            
            # Check dashboard was copied
            dest_dashboard = os.path.join(temp_dir, "reports", "confidence_dashboard.png")
            assert os.path.exists(dest_dashboard)
    
    @pytest.mark.asyncio
    async def test_analysis_summary_creation(self, packager, sample_results):
        """Test creation of analysis summary."""
        stats = {
            "pages_count": 2,
            "tables_count": 1,
            "confidence_score": 0.95,
            "processing_time": 5.3
        }
        
        summary = packager._create_analysis_summary(sample_results, stats)
        
        assert summary["document_analysis"]["pages_analyzed"] == 2
        assert summary["document_analysis"]["tables_extracted"] == 1
        assert summary["document_analysis"]["average_confidence"] == 0.95
        assert summary["content_statistics"]["total_characters"] == 1500
        assert summary["extraction_details"]["model_used"] == "prebuilt-layout"
        assert len(summary["table_details"]) == 1
        assert summary["table_details"][0]["rows"] == 3


class TestTranscriptionResultPackager:
    """Test suite for Transcription ResultPackager."""
    
    @pytest.fixture
    def mock_file_handler(self):
        """Create mock FileHandler."""
        handler = Mock(spec=FileHandler)
        handler.upload_to_blob = AsyncMock(return_value="https://test.blob.core.windows.net/test.zip")
        return handler
    
    @pytest.fixture
    def packager(self, mock_file_handler):
        """Create Transcription packager instance."""
        return TranscriptionResultPackager(mock_file_handler)
    
    @pytest.fixture
    def sample_results(self):
        """Create sample Transcription results."""
        return {
            "transcript_text": "[00:00-01:00][Speaker 1] This is the transcribed text.",
            "transcript_srt": "1\n00:00:00,000 --> 00:01:00,000\nThis is the transcribed text.",
            "transcript_vtt": "WEBVTT\n\n00:00:00.000 --> 00:01:00.000\nThis is the transcribed text.",
            "transcript_json": {
                "segments": [
                    {
                        "speaker": "Speaker 1",
                        "start": 0,
                        "end": 60,
                        "text": "This is the transcribed text."
                    }
                ]
            },
            "speaker_analysis": "Speaker Analysis Report\n======================\n",
            "transcript_summary": "Transcription Summary\n===================\n",
            "duration": 120.5,
            "speakers_count": 2,
            "total_words": 500,
            "average_confidence": 0.92,
            "audio_format": "wav",
            "audio_channels": 2,
            "sample_rate": 16000,
            "language": "en-US",
            "speaker_stats": {
                "Speaker 1": {
                    "speaking_time": 70,
                    "percentage": 58.3,
                    "words": 300,
                    "phrases": 15,
                    "confidence": 0.93
                },
                "Speaker 2": {
                    "speaking_time": 50,
                    "percentage": 41.7,
                    "words": 200,
                    "phrases": 10,
                    "confidence": 0.91
                }
            }
        }
    
    @pytest.mark.asyncio
    async def test_package_transcription_results(self, packager, sample_results):
        """Test packaging of Transcription results."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create standard directory structure first
            packager._create_standard_structure(temp_dir)
            
            metadata = {"processing_time": 15.2}
            
            stats = await packager._package_service_results(
                temp_dir, sample_results, "audio.wav", metadata
            )
            
            # Check statistics
            assert stats["duration_seconds"] == 120.5
            assert stats["speakers_count"] == 2
            assert stats["total_words"] == 500
            assert stats["confidence_score"] == 0.92
            assert stats["files_count"] > 0
            
            # Check transcript files
            txt_path = os.path.join(temp_dir, "processed", "audio_transcript.txt")
            assert os.path.exists(txt_path)
            
            srt_path = os.path.join(temp_dir, "processed", "audio_transcript.srt")
            assert os.path.exists(srt_path)
            
            vtt_path = os.path.join(temp_dir, "processed", "audio_transcript.vtt")
            assert os.path.exists(vtt_path)
            
            json_path = os.path.join(temp_dir, "processed", "audio_transcript_detailed.json")
            assert os.path.exists(json_path)
            
            # Check analysis report
            report_path = os.path.join(temp_dir, "reports", "transcription_analysis.json")
            assert os.path.exists(report_path)
            with open(report_path, 'r') as f:
                report = json.load(f)
            assert report["transcription_summary"]["duration_seconds"] == 120.5
            assert len(report["speaker_statistics"]) == 2
    
    @pytest.mark.asyncio
    async def test_duration_formatting(self, packager):
        """Test duration formatting."""
        assert packager._format_duration(0) == "0s"
        assert packager._format_duration(45) == "45s"
        assert packager._format_duration(90) == "1m 30s"
        assert packager._format_duration(3665) == "1h 1m 5s"
        assert packager._format_duration(7200) == "2h"
    
    @pytest.mark.asyncio
    async def test_analysis_report_creation(self, packager, sample_results):
        """Test creation of analysis report."""
        stats = {
            "duration_seconds": 120.5,
            "speakers_count": 2,
            "total_words": 500,
            "confidence_score": 0.92,
            "processing_time": 15.2
        }
        
        report = packager._create_analysis_report(sample_results, stats)
        
        assert report["transcription_summary"]["duration_formatted"] == "2m 0s"
        assert report["transcription_summary"]["speakers_detected"] == 2
        assert report["audio_properties"]["format"] == "wav"
        assert report["transcription_details"]["language"] == "en-US"
        assert len(report["speaker_statistics"]) == 2
        assert report["speaker_statistics"][0]["speaker"] == "Speaker 1"
        assert report["speaker_statistics"][0]["speaking_time_percentage"] == 58.3
    
    @pytest.mark.asyncio
    async def test_package_with_speaker_metadata(self, packager):
        """Test packaging with detailed speaker metadata."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create standard directory structure first
            packager._create_standard_structure(temp_dir)
            
            results = {
                "duration": 60,
                "speaker_metadata": {
                    "speakers": ["Speaker 1", "Speaker 2"],
                    "confidence_threshold": 0.8,
                    "diarization_model": "advanced"
                }
            }
            
            await packager._package_service_results(
                temp_dir, results, "audio.mp3", {}
            )
            
            # Check speaker metadata was saved
            metadata_path = os.path.join(temp_dir, "metadata", "speaker_metadata.json")
            assert os.path.exists(metadata_path)


class TestTranslationResultPackager:
    """Test suite for Translation ResultPackager."""
    
    @pytest.fixture
    def mock_file_handler(self):
        """Create mock FileHandler."""
        handler = Mock(spec=FileHandler)
        handler.upload_to_blob = AsyncMock(return_value="https://test.blob.core.windows.net/test.zip")
        return handler
    
    @pytest.fixture
    def packager(self, mock_file_handler):
        """Create Translation packager instance."""
        return TranslationResultPackager(mock_file_handler)
    
    @pytest.fixture
    def sample_text_results(self):
        """Create sample text translation results."""
        return {
            "type": "text",
            "original_text": "Hello world",
            "translated_text": "Hola mundo",
            "source_language": "en",
            "target_language": "es",
            "detected_language": "en",
            "characters_count": 11,
            "words_count": 2,
            "confidence": 0.99,
            "language_detection": {
                "language": "en",
                "confidence": 0.99,
                "alternatives": [
                    {"language": "nl", "confidence": 0.01}
                ]
            }
        }
    
    @pytest.fixture
    def sample_document_results(self):
        """Create sample document translation results."""
        return {
            "type": "document",
            "source_language": "en",
            "target_language": "fr",
            "characters_count": 5000,
            "pages_count": 3,
            "document_format": "docx",
            "original_text": "Original document text...",
            "translated_text": "Texte du document traduit..."
        }
    
    @pytest.mark.asyncio
    async def test_package_text_translation(self, packager, sample_text_results):
        """Test packaging of text translation results."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create standard directory structure first
            packager._create_standard_structure(temp_dir)
            
            metadata = {"processing_time": 0.5, "job_id": "text-123"}
            
            stats = await packager._package_service_results(
                temp_dir, sample_text_results, "text_input.txt", metadata
            )
            
            # Check statistics
            assert stats["translation_type"] == "text"
            assert stats["source_language"] == "en"
            assert stats["target_language"] == "es"
            assert stats["characters_translated"] == 11
            
            # Check text files
            original_path = os.path.join(temp_dir, "original", "original_text.txt")
            assert os.path.exists(original_path)
            with open(original_path, 'r') as f:
                assert f.read() == "Hello world"
            
            translated_path = os.path.join(temp_dir, "processed", "translated_text_es.txt")
            assert os.path.exists(translated_path)
            with open(translated_path, 'r') as f:
                assert f.read() == "Hola mundo"
            
            # Check language detection
            detection_path = os.path.join(temp_dir, "metadata", "language_detection.json")
            assert os.path.exists(detection_path)
            
            # Check reports
            report_path = os.path.join(temp_dir, "reports", "translation_report.json")
            assert os.path.exists(report_path)
            
            summary_path = os.path.join(temp_dir, "reports", "translation_summary.txt")
            assert os.path.exists(summary_path)
    
    @pytest.mark.asyncio
    async def test_package_document_translation(self, packager, sample_document_results):
        """Test packaging of document translation results."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create standard directory structure first
            packager._create_standard_structure(temp_dir)
            
            # Create mock document files
            original_doc = os.path.join(temp_dir, "original.docx")
            with open(original_doc, 'wb') as f:
                f.write(b"mock docx content")
            
            translated_doc = os.path.join(temp_dir, "translated.docx")
            with open(translated_doc, 'wb') as f:
                f.write(b"mock translated docx")
            
            results = sample_document_results.copy()
            results["original_file_path"] = original_doc
            results["translated_file_path"] = translated_doc
            
            metadata = {"processing_time": 3.2}
            
            stats = await packager._package_service_results(
                temp_dir, results, "document.docx", metadata
            )
            
            # Check document files
            orig_dest = os.path.join(temp_dir, "original", "document.docx")
            assert os.path.exists(orig_dest)
            
            trans_dest = os.path.join(temp_dir, "processed", "document_fr.docx")
            assert os.path.exists(trans_dest)
            
            # Check text extracts
            orig_text_path = os.path.join(temp_dir, "metadata", "document_original_text.txt")
            assert os.path.exists(orig_text_path)
            
            trans_text_path = os.path.join(temp_dir, "metadata", "document_translated_text.txt")
            assert os.path.exists(trans_text_path)
    
    @pytest.mark.asyncio
    async def test_translation_report_creation(self, packager, sample_text_results):
        """Test creation of translation report."""
        stats = {
            "translation_type": "text",
            "source_language": "en",
            "target_language": "es",
            "characters_translated": 11,
            "confidence_score": 0.99,
            "processing_time": 0.5
        }
        metadata = {"formality": "informal", "profanity_action": "marked"}
        
        report = packager._create_translation_report(
            sample_text_results, stats, metadata
        )
        
        assert report["translation_summary"]["type"] == "text"
        assert report["translation_summary"]["detected_language"] == "en"
        assert report["translation_details"]["formality"] == "informal"
        assert report["language_detection"]["confidence"] == 0.99
        assert len(report["language_detection"]["alternatives"]) == 1
    
    @pytest.mark.asyncio
    async def test_summary_text_creation(self, packager, sample_text_results):
        """Test creation of human-readable summary."""
        stats = {
            "translation_type": "text",
            "source_language": "en",
            "target_language": "es",
            "characters_translated": 11,
            "processing_time": 0.5
        }
        metadata = {
            "timestamp": "2024-01-01T12:00:00",
            "job_id": "test-123"
        }
        
        summary = packager._create_summary_text(
            sample_text_results, stats, metadata
        )
        
        assert "TRANSLATION SUMMARY" in summary
        assert "Source Language: English" in summary
        assert "Target Language: Spanish" in summary
        assert "Characters Translated: 11" in summary
        assert "Job ID: test-123" in summary
    
    @pytest.mark.asyncio
    async def test_language_formatting(self, packager):
        """Test language code formatting."""
        assert packager._format_language("en") == "English"
        assert packager._format_language("es") == "Spanish"
        assert packager._format_language("fr") == "French"
        assert packager._format_language("auto-detect") == "Auto-Detect"
        assert packager._format_language("xyz") == "XYZ"  # Unknown code