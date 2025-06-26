"""
Integration tests for ResultPackager implementations.

Tests the complete flow from results to downloadable ZIP packages,
including interaction with file handlers and blob storage.
"""
import os
import json
import zipfile
import tempfile
from unittest.mock import Mock, AsyncMock, patch, MagicMock
import pytest

from services.document_intelligence.result_packager import DocumentIntelligenceResultPackager
from services.transcription.result_packager import TranscriptionResultPackager
from services.translation.result_packager import TranslationResultPackager
from utils.file_handler import FileHandler


class TestResultPackagerIntegration:
    """Integration tests for all ResultPackager implementations."""
    
    def _verify_zip_contents(self, mock_file_handler, expected_files):
        """Helper to verify ZIP contents from mock."""
        call_args = mock_file_handler.upload_to_blob.call_args
        blob_path = call_args[0][1]
        saved_zip = mock_file_handler.saved_zips[blob_path]
        namelist = saved_zip['namelist']
        
        for expected_file in expected_files:
            assert any(expected_file in f for f in namelist), f"Expected {expected_file} in ZIP"
        
        return saved_zip
    
    @pytest.fixture
    def mock_file_handler(self):
        """Create mock FileHandler with realistic behavior."""
        handler = Mock(spec=FileHandler)
        handler.saved_zips = {}  # Store ZIP contents for verification
        
        # Mock upload to capture the ZIP file
        async def mock_upload(zip_path, blob_path):
            # Verify ZIP exists and is valid
            assert os.path.exists(zip_path)
            with zipfile.ZipFile(zip_path, 'r') as zf:
                assert zf.testzip() is None  # No errors in ZIP
                # Save ZIP contents for later verification
                handler.saved_zips[blob_path] = {
                    'path': zip_path,
                    'namelist': zf.namelist(),
                    'content': {}
                }
                # Extract some key files for verification
                for name in zf.namelist():
                    if name.endswith('.json') or name.endswith('.md') or name.endswith('.txt'):
                        try:
                            handler.saved_zips[blob_path]['content'][name] = zf.read(name).decode('utf-8')
                        except:
                            pass
            return f"https://test.blob.core.windows.net/{blob_path}"
        
        handler.upload_to_blob = AsyncMock(side_effect=mock_upload)
        return handler
    
    @pytest.mark.asyncio
    async def test_document_intelligence_full_flow(self, mock_file_handler):
        """Test complete Document Intelligence packaging flow."""
        packager = DocumentIntelligenceResultPackager(mock_file_handler)
        
        # Create realistic results
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create mock files
            dashboard_path = os.path.join(temp_dir, "dashboard.png")
            with open(dashboard_path, 'wb') as f:
                f.write(b"PNG\x89\x50\x4E\x47")  # PNG header
            
            excel_path = os.path.join(temp_dir, "tables.xlsx")
            with open(excel_path, 'wb') as f:
                f.write(b"PK")  # ZIP/Office header
            
            csv_path = os.path.join(temp_dir, "table1.csv")
            with open(csv_path, 'w') as f:
                f.write("Column1,Column2,Column3\n")
                f.write("Value1,Value2,Value3\n")
                f.write("Data1,Data2,Data3\n")
            
            results = {
                "markdown_content": "# Analysis Results\n\n## Summary\n\nThis document contains **important** information.\n\n## Tables\n\nSee extracted tables below.",
                "page_markdowns": [
                    "# Page 1\n\nFirst page with introduction.",
                    "# Page 2\n\nSecond page with data tables."
                ],
                "pages_count": 2,
                "tables_count": 1,
                "average_confidence": 0.945,
                "total_characters": 1234,
                "total_words": 256,
                "total_lines": 45,
                "model_used": "prebuilt-layout",
                "confidence_dashboard_path": dashboard_path,
                "excel_file_path": excel_path,
                "table_csv_files": [
                    {
                        "path": csv_path,
                        "filename": "page1_table0.csv",
                        "page": 1
                    }
                ],
                "table_details": [
                    {
                        "page": 1,
                        "rows": 3,
                        "columns": 3,
                        "cells": 9,
                        "confidence": 0.97
                    }
                ],
                "confidence_stats": {
                    "min": 0.89,
                    "max": 0.99,
                    "mean": 0.945,
                    "std": 0.032
                },
                "azure_response": {
                    "api_version": "2023-07-31",
                    "model_id": "prebuilt-layout",
                    "content": "raw content here"
                }
            }
            
            metadata = {
                "processing_time": 8.75,
                "job_id": "doc-intel-test-123",
                "user": "test_user"
            }
            
            # Create package
            download_url = await packager.create_package(
                "doc-intel-test-123",
                results,
                "financial_report.pdf",
                metadata
            )
            
            # Verify result
            assert download_url == "https://test.blob.core.windows.net/results/doc-intel-test-123/doc-intel-test-123_document_intelligence_results.zip"
            
            # Verify upload was called correctly
            mock_file_handler.upload_to_blob.assert_called_once()
            call_args = mock_file_handler.upload_to_blob.call_args
            
            # Verify ZIP contents from saved data
            blob_path = call_args[0][1]
            saved_zip = mock_file_handler.saved_zips[blob_path]
            namelist = saved_zip['namelist']
            content = saved_zip['content']
            
            # Verify structure
            assert 'summary.json' in namelist
            assert any('processed/financial_report_document.md' in f for f in namelist)
            assert any('processed/pages/financial_report_page1.md' in f for f in namelist)
            assert any('processed/pages/financial_report_page2.md' in f for f in namelist)
            assert any('processed/tables/csv/page1_table0.csv' in f for f in namelist)
            assert any('processed/financial_report_tables.xlsx' in f for f in namelist)
            assert any('reports/confidence_dashboard.png' in f for f in namelist)
            assert any('reports/analysis_summary.json' in f for f in namelist)
            assert any('metadata/azure_response.json' in f for f in namelist)
            assert any('metadata/confidence_statistics.json' in f for f in namelist)
            
            # Verify summary.json content
            summary_content = content.get('summary.json')
            if summary_content:
                summary = json.loads(summary_content)
                assert summary["job_id"] == "doc-intel-test-123"
                assert summary["service"] == "document_intelligence"
                assert summary["original_filename"] == "financial_report.pdf"
                assert summary["statistics"]["pages_count"] == 2
                assert summary["statistics"]["confidence_score"] == 0.945
            
            # Verify markdown content
            md_file = next((f for f in namelist if 'processed/financial_report_document.md' in f), None)
            if md_file and md_file in content:
                md_content = content[md_file]
                assert "# Analysis Results" in md_content
                assert "**important**" in md_content
    
    @pytest.mark.asyncio
    async def test_transcription_full_flow(self, mock_file_handler):
        """Test complete Transcription packaging flow."""
        packager = TranscriptionResultPackager(mock_file_handler)
        
        # Create realistic transcription results
        results = {
            "transcript_text": """[00:00-01:00][Speaker 1] Good morning everyone. Today we'll be discussing the quarterly results.
[01:00-02:00][Speaker 2] Thank you for joining. The numbers look very promising.
[02:00-03:00][Speaker 1] Indeed, we've seen significant growth across all sectors.""",
            "transcript_srt": """1
00:00:00,000 --> 00:01:00,000
[Speaker 1] Good morning everyone. Today we'll be discussing the quarterly results.

2
00:01:00,000 --> 00:02:00,000
[Speaker 2] Thank you for joining. The numbers look very promising.

3
00:02:00,000 --> 00:03:00,000
[Speaker 1] Indeed, we've seen significant growth across all sectors.""",
            "transcript_vtt": """WEBVTT

00:00:00.000 --> 00:01:00.000
<v Speaker 1>Good morning everyone. Today we'll be discussing the quarterly results.

00:01:00.000 --> 00:02:00.000
<v Speaker 2>Thank you for joining. The numbers look very promising.

00:02:00.000 --> 00:03:00.000
<v Speaker 1>Indeed, we've seen significant growth across all sectors.""",
            "transcript_json": {
                "duration": 180.0,
                "segments": [
                    {
                        "start": 0,
                        "end": 60,
                        "speaker": "Speaker 1",
                        "text": "Good morning everyone. Today we'll be discussing the quarterly results.",
                        "confidence": 0.95
                    },
                    {
                        "start": 60,
                        "end": 120,
                        "speaker": "Speaker 2",
                        "text": "Thank you for joining. The numbers look very promising.",
                        "confidence": 0.93
                    },
                    {
                        "start": 120,
                        "end": 180,
                        "speaker": "Speaker 1",
                        "text": "Indeed, we've seen significant growth across all sectors.",
                        "confidence": 0.94
                    }
                ]
            },
            "speaker_analysis": """SPEAKER ANALYSIS REPORT
=======================

Total Duration: 3 minutes
Speakers Identified: 2

Speaker 1:
- Speaking Time: 2 minutes (66.7%)
- Words Spoken: 24
- Average Confidence: 94.5%

Speaker 2:
- Speaking Time: 1 minute (33.3%)
- Words Spoken: 11
- Average Confidence: 93.0%

Speaker Transitions: 2
Average Turn Duration: 1 minute""",
            "transcript_summary": """TRANSCRIPTION SUMMARY
====================

File: conference_call.wav
Duration: 3 minutes
Language: en-US
Speakers: 2
Total Words: 35
Average Confidence: 94.0%

Processing completed successfully.""",
            "duration": 180.0,
            "speakers_count": 2,
            "total_words": 35,
            "average_confidence": 0.94,
            "audio_format": "wav",
            "audio_channels": 1,
            "sample_rate": 16000,
            "bitrate": 256000,
            "language": "en-US",
            "speaker_stats": {
                "Speaker 1": {
                    "speaking_time": 120,
                    "percentage": 66.7,
                    "words": 24,
                    "phrases": 2,
                    "confidence": 0.945
                },
                "Speaker 2": {
                    "speaking_time": 60,
                    "percentage": 33.3,
                    "words": 11,
                    "phrases": 1,
                    "confidence": 0.93
                }
            },
            "azure_response": {
                "recognitionStatus": "Success",
                "offset": 0,
                "duration": 180000000
            }
        }
        
        metadata = {
            "processing_time": 12.5,
            "job_id": "trans-test-456"
        }
        
        # Create package
        download_url = await packager.create_package(
            "trans-test-456",
            results,
            "conference_call.wav",
            metadata
        )
        
        # Verify result
        assert download_url == "https://test.blob.core.windows.net/results/trans-test-456/trans-test-456_transcription_results.zip"
        
        # Verify ZIP contents
        expected_files = [
            "processed/conference_call_transcript.txt",
            "processed/conference_call_transcript.srt",
            "processed/conference_call_transcript.vtt",
            "processed/conference_call_transcript_detailed.json",
            "reports/conference_call_speaker_analysis.txt",
            "reports/conference_call_transcript_summary.txt",
            "reports/transcription_analysis.json"
        ]
        saved_zip = self._verify_zip_contents(mock_file_handler, expected_files)
        
        # Verify analysis report content
        analysis_content = saved_zip['content'].get('reports/transcription_analysis.json')
        if analysis_content:
            analysis = json.loads(analysis_content)
            assert analysis["transcription_summary"]["duration_formatted"] == "3m 0s"
            assert analysis["transcription_summary"]["speakers_detected"] == 2
            assert len(analysis["speaker_statistics"]) == 2
    
    @pytest.mark.asyncio
    async def test_translation_full_flow_document(self, mock_file_handler):
        """Test complete Translation packaging flow for document translation."""
        packager = TranslationResultPackager(mock_file_handler)
        
        # Create mock document files
        with tempfile.TemporaryDirectory() as temp_dir:
            original_doc = os.path.join(temp_dir, "contract.docx")
            with open(original_doc, 'wb') as f:
                f.write(b"PK\x03\x04")  # DOCX header
            
            translated_doc = os.path.join(temp_dir, "contract_translated.docx")
            with open(translated_doc, 'wb') as f:
                f.write(b"PK\x03\x04")  # DOCX header
            
            results = {
                "type": "document",
                "original_file_path": original_doc,
                "translated_file_path": translated_doc,
                "original_text": "This is a legal contract between Party A and Party B.",
                "translated_text": "Ceci est un contrat légal entre la Partie A et la Partie B.",
                "source_language": "en",
                "target_language": "fr",
                "detected_language": "en",
                "characters_count": 52,
                "words_count": 11,
                "pages_count": 1,
                "document_format": "docx",
                "confidence": 0.98,
                "language_detection": {
                    "language": "en",
                    "confidence": 0.99,
                    "alternatives": []
                },
                "model": "standard",
                "formatting_preserved": True,
                "azure_response": {
                    "translations": [{
                        "text": "Ceci est un contrat légal entre la Partie A et la Partie B.",
                        "to": "fr"
                    }]
                }
            }
            
            metadata = {
                "processing_time": 2.1,
                "job_id": "trans-doc-789",
                "timestamp": "2024-01-15T10:30:00Z",
                "formality": "formal",
                "preserve_formatting": True
            }
            
            # Create package
            download_url = await packager.create_package(
                "trans-doc-789",
                results,
                "contract.docx",
                metadata
            )
            
            # Verify result
            assert "trans-doc-789_translation_results.zip" in download_url
            
            # Extract and verify ZIP contents
            call_args = mock_file_handler.upload_to_blob.call_args
            zip_path = call_args[0][0]
            
            with tempfile.TemporaryDirectory() as extract_dir:
                with zipfile.ZipFile(zip_path, 'r') as zf:
                    zf.extractall(extract_dir)
                
                # Verify document files
                assert os.path.exists(os.path.join(extract_dir, "original", "contract.docx"))
                assert os.path.exists(os.path.join(extract_dir, "processed", "contract_fr.docx"))
                
                # Verify text extracts
                assert os.path.exists(os.path.join(extract_dir, "metadata", "contract_original_text.txt"))
                assert os.path.exists(os.path.join(extract_dir, "metadata", "contract_translated_text.txt"))
                
                # Verify translation summary
                with open(os.path.join(extract_dir, "reports", "translation_summary.txt"), 'r') as f:
                    summary_text = f.read()
                assert "Translation Type: Document" in summary_text
                assert "Source Language: English" in summary_text
                assert "Target Language: French" in summary_text
                assert "Formality: formal" in summary_text
    
    @pytest.mark.asyncio
    async def test_error_recovery_and_cleanup(self, mock_file_handler):
        """Test that temporary files are cleaned up even on errors."""
        # Make upload fail
        mock_file_handler.upload_to_blob.side_effect = Exception("Network error")
        
        packager = DocumentIntelligenceResultPackager(mock_file_handler)
        
        results = {
            "markdown_content": "Test content",
            "pages_count": 1
        }
        
        with pytest.raises(Exception) as exc_info:
            await packager.create_package(
                "error-job-999",
                results,
                "test.pdf"
            )
        
        assert "Network error" in str(exc_info.value)
        
        # Verify temp directory was cleaned up
        assert not os.path.exists("/tmp/error-job-999_packaging")
    
    @pytest.mark.asyncio
    async def test_large_file_handling(self, mock_file_handler):
        """Test handling of large results with many files."""
        packager = DocumentIntelligenceResultPackager(mock_file_handler)
        
        # Create results with many pages
        page_markdowns = []
        for i in range(50):
            page_markdowns.append(f"# Page {i+1}\n\n" + "Content " * 100)
        
        results = {
            "markdown_content": "# Large Document\n\n" + "Section " * 1000,
            "page_markdowns": page_markdowns,
            "pages_count": 50,
            "tables_count": 25,
            "average_confidence": 0.92,
            "total_characters": 50000,
            "total_words": 8500,
            "table_details": [
                {"page": i, "rows": 10, "columns": 5, "cells": 50, "confidence": 0.9}
                for i in range(1, 26)
            ]
        }
        
        # Create package
        download_url = await packager.create_package(
            "large-doc-test",
            results,
            "large_document.pdf",
            {"processing_time": 45.2}
        )
        
        # Verify successful completion
        assert "large-doc-test_document_intelligence_results.zip" in download_url
        
        # Verify ZIP was created successfully
        call_args = mock_file_handler.upload_to_blob.call_args
        zip_path = call_args[0][0]
        
        with zipfile.ZipFile(zip_path, 'r') as zf:
            files = zf.namelist()
            # Should have 50 page files plus other standard files
            page_files = [f for f in files if "pages/large_document_page" in f]
            assert len(page_files) == 50
    
    @pytest.mark.asyncio  
    async def test_unicode_content_preservation(self, mock_file_handler):
        """Test that unicode content is preserved correctly."""
        packager = TranslationResultPackager(mock_file_handler)
        
        results = {
            "type": "text",
            "original_text": "Hello 世界 🌍 Café résumé naïve",
            "translated_text": "Bonjour 世界 🌍 Café résumé naïve",
            "source_language": "en",
            "target_language": "fr",
            "characters_count": 30,
            "confidence": 0.95
        }
        
        download_url = await packager.create_package(
            "unicode-test",
            results,
            "unicode.txt",
            {}
        )
        
        # Extract and verify content
        call_args = mock_file_handler.upload_to_blob.call_args
        zip_path = call_args[0][0]
        
        with tempfile.TemporaryDirectory() as extract_dir:
            with zipfile.ZipFile(zip_path, 'r') as zf:
                zf.extractall(extract_dir)
            
            # Verify unicode is preserved
            with open(os.path.join(extract_dir, "original", "original_text.txt"), 'r', encoding='utf-8') as f:
                original = f.read()
            assert "世界" in original
            assert "🌍" in original
            assert "naïve" in original