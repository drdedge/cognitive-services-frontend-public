"""
Azure service mocks for comprehensive testing.
"""
from unittest.mock import Mock, AsyncMock, MagicMock
from typing import Dict, List, Any, Optional
import json
from datetime import datetime, timedelta
import asyncio


class MockDocumentIntelligenceClient:
    """Mock Azure Document Intelligence client for testing."""
    
    def __init__(self, scenario: str = "success"):
        self.scenario = scenario
        self._call_count = 0
    
    def begin_analyze_document(self, model_id: str, document, **kwargs):
        """Mock document analysis with different scenarios."""
        self._call_count += 1
        
        if self.scenario == "success":
            return self._create_successful_poller()
        elif self.scenario == "large_document":
            return self._create_large_document_poller()
        elif self.scenario == "table_extraction":
            return self._create_table_extraction_poller()
        elif self.scenario == "low_confidence":
            return self._create_low_confidence_poller()
        elif self.scenario == "service_error":
            raise Exception("Azure service temporarily unavailable")
        elif self.scenario == "timeout":
            return self._create_timeout_poller()
        else:
            return self._create_successful_poller()
    
    def _create_successful_poller(self):
        """Create a successful analysis poller."""
        mock_poller = Mock()
        mock_result = Mock()
        
        # Mock document content
        mock_result.content = "This is sample extracted text from the document."
        
        # Mock pages
        mock_page = Mock()
        mock_page.page_number = 1
        mock_page.width = 8.5
        mock_page.height = 11.0
        mock_page.words = [
            Mock(content="This", confidence=0.95, bounding_box=[1.0, 1.0, 1.5, 1.2]),
            Mock(content="is", confidence=0.92, bounding_box=[1.6, 1.0, 1.8, 1.2]),
            Mock(content="sample", confidence=0.94, bounding_box=[1.9, 1.0, 2.4, 1.2])
        ]
        mock_result.pages = [mock_page]
        
        # Mock tables (empty for basic scenario)
        mock_result.tables = []
        
        # Mock poller behavior
        mock_poller.done.return_value = True
        mock_poller.result.return_value = mock_result
        mock_poller.status = "succeeded"
        
        return mock_poller
    
    def _create_table_extraction_poller(self):
        """Create poller with table extraction results."""
        mock_poller = Mock()
        mock_result = Mock()
        
        # Mock table
        mock_table = Mock()
        mock_table.row_count = 3
        mock_table.column_count = 2
        mock_table.cells = [
            Mock(content="Header 1", row_index=0, column_index=0, confidence=0.98),
            Mock(content="Header 2", row_index=0, column_index=1, confidence=0.96),
            Mock(content="Data 1", row_index=1, column_index=0, confidence=0.94),
            Mock(content="Data 2", row_index=1, column_index=1, confidence=0.92),
            Mock(content="Data 3", row_index=2, column_index=0, confidence=0.89),
            Mock(content="Data 4", row_index=2, column_index=1, confidence=0.91)
        ]
        
        mock_result.tables = [mock_table]
        mock_result.content = "Document with table data"
        mock_result.pages = [Mock(page_number=1)]
        
        mock_poller.done.return_value = True
        mock_poller.result.return_value = mock_result
        
        return mock_poller
    
    def _create_large_document_poller(self):
        """Create poller for large document processing."""
        mock_poller = Mock()
        mock_result = Mock()
        
        # Mock 100 pages
        mock_pages = []
        for i in range(100):
            mock_page = Mock()
            mock_page.page_number = i + 1
            mock_page.content = f"Page {i+1} content"
            mock_pages.append(mock_page)
        
        mock_result.pages = mock_pages
        mock_result.content = "Large document with 100 pages"
        mock_result.tables = []
        
        # Simulate progressive completion
        call_count = [0]
        def check_done():
            call_count[0] += 1
            return call_count[0] >= 3  # Done after 3 checks
        
        mock_poller.done = check_done
        mock_poller.result.return_value = mock_result
        
        return mock_poller
    
    def _create_low_confidence_poller(self):
        """Create poller with low confidence results."""
        mock_poller = Mock()
        mock_result = Mock()
        
        # Mock low confidence words
        mock_page = Mock()
        mock_page.words = [
            Mock(content="unclear", confidence=0.45),
            Mock(content="text", confidence=0.52),
            Mock(content="here", confidence=0.38)
        ]
        mock_result.pages = [mock_page]
        mock_result.content = "unclear text here"
        mock_result.tables = []
        
        mock_poller.done.return_value = True
        mock_poller.result.return_value = mock_result
        
        return mock_poller
    
    def _create_timeout_poller(self):
        """Create poller that simulates timeout."""
        mock_poller = Mock()
        mock_poller.done.return_value = False
        mock_poller.status = "running"
        mock_poller.result.side_effect = asyncio.TimeoutError("Analysis timeout")
        
        return mock_poller


class MockTranslatorClient:
    """Mock Azure Translator client for testing."""
    
    def __init__(self, scenario: str = "success"):
        self.scenario = scenario
        self._call_count = 0
    
    async def translate(self, text: List[str], target_languages: List[str], source_language: str = None, **kwargs):
        """Mock text translation."""
        self._call_count += 1
        
        if self.scenario == "success":
            return self._create_successful_translation(text, target_languages, source_language)
        elif self.scenario == "auto_detect":
            return self._create_auto_detect_translation(text, target_languages)
        elif self.scenario == "multiple_targets":
            return self._create_multi_target_translation(text, target_languages)
        elif self.scenario == "special_characters":
            return self._create_special_char_translation(text, target_languages)
        elif self.scenario == "rate_limit":
            from azure.core.exceptions import HttpResponseError
            response = Mock()
            response.status_code = 429
            response.headers = {"Retry-After": "60"}
            raise HttpResponseError(response=response)
        elif self.scenario == "service_error":
            raise Exception("Translator service temporarily unavailable")
        else:
            return self._create_successful_translation(text, target_languages, source_language)
    
    async def get_languages(self, **kwargs):
        """Mock get supported languages."""
        return {
            "translation": {
                "en": {"name": "English", "nativeName": "English"},
                "es": {"name": "Spanish", "nativeName": "Español"},
                "fr": {"name": "French", "nativeName": "Français"},
                "de": {"name": "German", "nativeName": "Deutsch"},
                "it": {"name": "Italian", "nativeName": "Italiano"},
                "pt": {"name": "Portuguese", "nativeName": "Português"},
                "zh": {"name": "Chinese Simplified", "nativeName": "中文"},
                "ja": {"name": "Japanese", "nativeName": "日本語"},
                "ko": {"name": "Korean", "nativeName": "한국어"},
                "ar": {"name": "Arabic", "nativeName": "العربية"}
            }
        }
    
    def _create_successful_translation(self, texts: List[str], target_languages: List[str], source_language: str):
        """Create successful translation response."""
        translations = []
        
        # Translation mappings
        translation_map = {
            ("en", "es"): {
                "Hello world": "Hola mundo",
                "This is a test": "Esta es una prueba",
                "Good morning": "Buenos días"
            },
            ("en", "fr"): {
                "Hello world": "Bonjour le monde",
                "This is a test": "Ceci est un test",
                "Good morning": "Bonjour"
            },
            ("es", "en"): {
                "Hola mundo": "Hello world",
                "Esta es una prueba": "This is a test",
                "Buenos días": "Good morning"
            }
        }
        
        for text in texts:
            text_translations = []
            for target_lang in target_languages:
                source_lang = source_language or "en"
                
                # Get translation from map or generate default
                key = (source_lang, target_lang)
                if key in translation_map and text in translation_map[key]:
                    translated_text = translation_map[key][text]
                else:
                    translated_text = f"[{target_lang.upper()}] {text}"
                
                text_translations.append({
                    "text": translated_text,
                    "to": target_lang
                })
            
            result = {
                "translations": text_translations
            }
            
            # Add detected language if not provided
            if not source_language:
                result["detectedLanguage"] = {
                    "language": "en",
                    "score": 0.95
                }
            
            translations.append(result)
        
        return translations
    
    def _create_auto_detect_translation(self, texts: List[str], target_languages: List[str]):
        """Create translation with language auto-detection."""
        # Language detection patterns
        detection_map = {
            "你好": ("zh", 0.99),
            "こんにちは": ("ja", 0.98),
            "Bonjour": ("fr", 0.96),
            "Hola": ("es", 0.97),
            "Guten Tag": ("de", 0.95)
        }
        
        translations = []
        for text in texts:
            # Detect language
            detected_lang = "en"
            confidence = 0.90
            
            for pattern, (lang, conf) in detection_map.items():
                if pattern in text:
                    detected_lang = lang
                    confidence = conf
                    break
            
            # Create translation
            text_translations = []
            for target_lang in target_languages:
                if detected_lang == "zh" and target_lang == "en":
                    translated = "Hello"
                elif detected_lang == "ja" and target_lang == "en":
                    translated = "Hello"
                elif detected_lang == "fr" and target_lang == "en":
                    translated = "Hello"
                else:
                    translated = f"[Translated from {detected_lang}] {text}"
                
                text_translations.append({
                    "text": translated,
                    "to": target_lang
                })
            
            translations.append({
                "translations": text_translations,
                "detectedLanguage": {
                    "language": detected_lang,
                    "score": confidence
                }
            })
        
        return translations
    
    def _create_multi_target_translation(self, texts: List[str], target_languages: List[str]):
        """Create translation to multiple target languages."""
        return self._create_successful_translation(texts, target_languages, "en")
    
    def _create_special_char_translation(self, texts: List[str], target_languages: List[str]):
        """Create translation preserving special characters."""
        translations = []
        for text in texts:
            text_translations = []
            for target_lang in target_languages:
                # Preserve emojis, symbols, etc.
                if "👋" in text:
                    translated = text.replace("Hello", "Hola" if target_lang == "es" else "Bonjour")
                elif "€" in text:
                    translated = text  # Keep currency symbols
                elif "@" in text:
                    translated = text  # Keep email addresses
                else:
                    translated = f"[{target_lang.upper()}] {text}"
                
                text_translations.append({
                    "text": translated,
                    "to": target_lang
                })
            
            translations.append({
                "translations": text_translations,
                "detectedLanguage": {
                    "language": "en",
                    "score": 0.92
                }
            })
        
        return translations


class MockSpeechServiceClient:
    """Mock Azure Speech Service client for testing."""
    
    def __init__(self, scenario: str = "success"):
        self.scenario = scenario
        self._call_count = 0
    
    async def recognize_once_async(self, audio_config, **kwargs):
        """Mock single-shot speech recognition."""
        self._call_count += 1
        
        if self.scenario == "success":
            return self._create_successful_recognition()
        elif self.scenario == "multiple_speakers":
            return self._create_diarized_recognition()
        elif self.scenario == "low_quality":
            return self._create_low_quality_recognition()
        elif self.scenario == "no_speech":
            return self._create_no_speech_recognition()
        elif self.scenario == "partial_results":
            return self._create_partial_recognition()
        elif self.scenario == "service_error":
            raise Exception("Speech service temporarily unavailable")
        else:
            return self._create_successful_recognition()
    
    async def start_continuous_recognition_async(self, **kwargs):
        """Mock continuous recognition start."""
        pass
    
    async def stop_continuous_recognition_async(self, **kwargs):
        """Mock continuous recognition stop."""
        pass
    
    def _create_successful_recognition(self):
        """Create successful recognition result."""
        mock_result = Mock()
        mock_result.text = "This is a clear audio transcription with high confidence."
        mock_result.reason = "RecognizedSpeech"
        mock_result.duration = 180000000  # 18 seconds in ticks
        
        # Mock detailed JSON result
        json_result = {
            "NBest": [{
                "Confidence": 0.92,
                "Lexical": "this is a clear audio transcription with high confidence",
                "ITN": "this is a clear audio transcription with high confidence",
                "MaskedITN": "this is a clear audio transcription with high confidence",
                "Display": "This is a clear audio transcription with high confidence.",
                "Words": [
                    {"Word": "This", "Offset": 0, "Duration": 5000000, "Confidence": 0.95},
                    {"Word": "is", "Offset": 5000000, "Duration": 2000000, "Confidence": 0.94},
                    {"Word": "a", "Offset": 7000000, "Duration": 1000000, "Confidence": 0.89},
                    {"Word": "clear", "Offset": 8000000, "Duration": 4000000, "Confidence": 0.96}
                ]
            }]
        }
        
        mock_result.properties = {
            "SpeechServiceResponse_JsonResult": json.dumps(json_result)
        }
        
        return mock_result
    
    def _create_diarized_recognition(self):
        """Create recognition result with speaker diarization."""
        mock_result = Mock()
        mock_result.text = "Speaker one says hello. Speaker two responds with greeting."
        mock_result.reason = "RecognizedSpeech"
        
        # Mock diarization data
        json_result = {
            "NBest": [{
                "Confidence": 0.88,
                "Display": "Speaker one says hello. Speaker two responds with greeting.",
                "Words": [
                    {"Word": "Speaker", "Speaker": 1, "Offset": 0, "Duration": 6000000},
                    {"Word": "one", "Speaker": 1, "Offset": 6000000, "Duration": 3000000},
                    {"Word": "says", "Speaker": 1, "Offset": 9000000, "Duration": 4000000},
                    {"Word": "hello", "Speaker": 1, "Offset": 13000000, "Duration": 5000000},
                    {"Word": "Speaker", "Speaker": 2, "Offset": 20000000, "Duration": 6000000},
                    {"Word": "two", "Speaker": 2, "Offset": 26000000, "Duration": 3000000},
                    {"Word": "responds", "Speaker": 2, "Offset": 29000000, "Duration": 8000000},
                    {"Word": "with", "Speaker": 2, "Offset": 37000000, "Duration": 4000000},
                    {"Word": "greeting", "Speaker": 2, "Offset": 41000000, "Duration": 8000000}
                ]
            }]
        }
        
        mock_result.properties = {
            "SpeechServiceResponse_JsonResult": json.dumps(json_result)
        }
        
        return mock_result
    
    def _create_low_quality_recognition(self):
        """Create recognition result for low quality audio."""
        mock_result = Mock()
        mock_result.text = "unclear audio with background noise"
        mock_result.reason = "RecognizedSpeech"
        
        json_result = {
            "NBest": [{
                "Confidence": 0.65,
                "Display": "unclear audio with background noise",
                "SNR": 8.5  # Low signal-to-noise ratio
            }]
        }
        
        mock_result.properties = {
            "SpeechServiceResponse_JsonResult": json.dumps(json_result)
        }
        
        return mock_result
    
    def _create_no_speech_recognition(self):
        """Create result when no speech is detected."""
        mock_result = Mock()
        mock_result.text = ""
        mock_result.reason = "NoMatch"
        
        mock_result.properties = {
            "SpeechServiceResponse_JsonResult": json.dumps({
                "RecognitionStatus": "NoMatch",
                "Offset": 0,
                "Duration": 0
            })
        }
        
        return mock_result
    
    def _create_partial_recognition(self):
        """Create partial recognition result."""
        mock_result = Mock()
        mock_result.text = "This is partial"
        mock_result.reason = "RecognizingSpeech"  # Partial result
        
        json_result = {
            "NBest": [{
                "Confidence": 0.75,
                "Display": "This is partial",
                "IsPartial": True
            }]
        }
        
        mock_result.properties = {
            "SpeechServiceResponse_JsonResult": json.dumps(json_result)
        }
        
        return mock_result


class MockBlobStorageClient:
    """Mock Azure Blob Storage client for testing."""
    
    def __init__(self, scenario: str = "success"):
        self.scenario = scenario
        self._blobs = {}  # In-memory blob storage
        self._call_count = 0
    
    def get_blob_client(self, container: str, blob: str):
        """Get mock blob client."""
        return MockBlobClient(self, container, blob, self.scenario)
    
    def get_container_client(self, container: str):
        """Get mock container client."""
        return MockContainerClient(self, container, self.scenario)


class MockBlobClient:
    """Mock Azure Blob client for testing."""
    
    def __init__(self, storage_client, container: str, blob_name: str, scenario: str = "success"):
        self.storage_client = storage_client
        self.container = container
        self.blob_name = blob_name
        self.scenario = scenario
        self._blob_key = f"{container}/{blob_name}"
    
    async def upload_blob(self, data, **kwargs):
        """Mock blob upload."""
        if self.scenario == "network_error":
            raise Exception("Network connection failed")
        elif self.scenario == "storage_full":
            raise Exception("Storage account quota exceeded")
        
        # Store blob data
        self.storage_client._blobs[self._blob_key] = {
            "data": data,
            "metadata": kwargs.get("metadata", {}),
            "uploaded_at": datetime.now().isoformat()
        }
        
        return Mock(etag="mock-etag-123")
    
    async def download_blob(self, **kwargs):
        """Mock blob download."""
        if self._blob_key not in self.storage_client._blobs:
            raise Exception("Blob not found")
        
        blob_data = self.storage_client._blobs[self._blob_key]
        
        mock_stream = Mock()
        mock_stream.readall.return_value = blob_data["data"]
        mock_stream.chunks.return_value = [blob_data["data"]]
        
        return mock_stream
    
    async def exists(self, **kwargs):
        """Check if blob exists."""
        return self._blob_key in self.storage_client._blobs
    
    async def delete_blob(self, **kwargs):
        """Delete blob."""
        if self._blob_key in self.storage_client._blobs:
            del self.storage_client._blobs[self._blob_key]
    
    async def set_blob_metadata(self, metadata: Dict[str, str], **kwargs):
        """Set blob metadata."""
        if self._blob_key in self.storage_client._blobs:
            self.storage_client._blobs[self._blob_key]["metadata"] = metadata
    
    async def get_blob_properties(self, **kwargs):
        """Get blob properties."""
        if self._blob_key not in self.storage_client._blobs:
            raise Exception("Blob not found")
        
        blob_data = self.storage_client._blobs[self._blob_key]
        
        mock_properties = Mock()
        mock_properties.metadata = blob_data.get("metadata", {})
        mock_properties.size = len(blob_data["data"]) if isinstance(blob_data["data"], bytes) else 1024
        mock_properties.last_modified = datetime.now()
        
        return mock_properties


class MockContainerClient:
    """Mock Azure Container client for testing."""
    
    def __init__(self, storage_client, container_name: str, scenario: str = "success"):
        self.storage_client = storage_client
        self.container_name = container_name
        self.scenario = scenario
    
    def list_blobs(self, **kwargs):
        """List blobs in container."""
        blobs = []
        
        for blob_key, blob_data in self.storage_client._blobs.items():
            container, blob_name = blob_key.split("/", 1)
            if container == self.container_name:
                mock_blob = Mock()
                mock_blob.name = blob_name
                mock_blob.size = len(blob_data["data"]) if isinstance(blob_data["data"], bytes) else 1024
                mock_blob.last_modified = datetime.now() - timedelta(days=1)
                blobs.append(mock_blob)
        
        return blobs
    
    async def delete_blob(self, blob_name: str, **kwargs):
        """Delete blob from container."""
        blob_key = f"{self.container_name}/{blob_name}"
        if blob_key in self.storage_client._blobs:
            del self.storage_client._blobs[blob_key]


def create_azure_mocks(services: List[str], scenarios: Dict[str, str] = None) -> Dict[str, Any]:
    """
    Create a set of Azure service mocks for testing.
    
    Args:
        services: List of services to mock (e.g., ['document_intelligence', 'translator'])
        scenarios: Dict mapping service names to test scenarios
    
    Returns:
        Dictionary of mock clients
    """
    scenarios = scenarios or {}
    mocks = {}
    
    if "document_intelligence" in services:
        scenario = scenarios.get("document_intelligence", "success")
        mocks["document_intelligence"] = MockDocumentIntelligenceClient(scenario)
    
    if "translator" in services:
        scenario = scenarios.get("translator", "success")
        mocks["translator"] = MockTranslatorClient(scenario)
    
    if "speech_service" in services:
        scenario = scenarios.get("speech_service", "success")
        mocks["speech_service"] = MockSpeechServiceClient(scenario)
    
    if "blob_storage" in services:
        scenario = scenarios.get("blob_storage", "success")
        mocks["blob_storage"] = MockBlobStorageClient(scenario)
    
    return mocks