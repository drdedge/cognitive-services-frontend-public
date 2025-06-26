"""
Pytest configuration and shared fixtures for the backend test suite.
"""
import pytest
import asyncio
from typing import AsyncGenerator, Generator
from unittest.mock import Mock, AsyncMock, MagicMock
from fastapi.testclient import TestClient
from httpx import AsyncClient
import tempfile
import os
from pathlib import Path

# Import the main FastAPI app
from main import app


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def test_client():
    """Create a test client for the FastAPI app."""
    return TestClient(app)


@pytest.fixture
async def async_client():
    """Create an async test client for the FastAPI app."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client


@pytest.fixture
def temp_upload_dir():
    """Create a temporary directory for file uploads."""
    with tempfile.TemporaryDirectory() as temp_dir:
        yield Path(temp_dir)


@pytest.fixture
def sample_files(temp_upload_dir):
    """Create sample test files."""
    files = {}
    
    # Create sample PDF
    pdf_path = temp_upload_dir / "sample.pdf"
    pdf_path.write_bytes(b"%PDF-1.4\n%fake pdf content\n")
    files["pdf"] = pdf_path
    
    # Create sample DOCX
    docx_path = temp_upload_dir / "sample.docx"
    docx_path.write_bytes(b"PK\x03\x04fake docx content")
    files["docx"] = docx_path
    
    # Create sample audio files
    wav_path = temp_upload_dir / "sample.wav"
    wav_path.write_bytes(b"RIFF\x00\x00\x00\x00WAVEfake wav content")
    files["wav"] = wav_path
    
    mp3_path = temp_upload_dir / "sample.mp3"
    mp3_path.write_bytes(b"ID3\x03\x00\x00\x00fake mp3 content")
    files["mp3"] = mp3_path
    
    # Create sample text file
    txt_path = temp_upload_dir / "sample.txt"
    txt_path.write_text("Hello world! This is a test file.")
    files["txt"] = txt_path
    
    return files


@pytest.fixture
def mock_azure_storage():
    """Mock Azure Blob Storage client."""
    mock_storage = Mock()
    mock_blob_service = Mock()
    mock_container = Mock()
    mock_blob = Mock()
    
    # Setup mock chain
    mock_storage.blob_service_client = mock_blob_service
    mock_blob_service.get_container_client.return_value = mock_container
    mock_container.get_blob_client.return_value = mock_blob
    
    # Mock blob operations
    mock_blob.upload_blob = AsyncMock()
    mock_blob.download_blob = AsyncMock()
    mock_blob.exists = AsyncMock(return_value=True)
    
    return mock_storage


@pytest.fixture
def mock_document_intelligence():
    """Mock Azure Document Intelligence client."""
    mock_client = Mock()
    mock_poller = Mock()
    mock_result = Mock()
    
    # Mock analysis result
    mock_result.tables = []
    mock_result.content = "Extracted text content"
    mock_result.pages = [Mock(page_number=1, width=8.5, height=11)]
    
    # Mock poller
    mock_poller.result = Mock(return_value=mock_result)
    mock_poller.done = Mock(return_value=True)
    
    # Mock begin_analyze_document
    mock_client.begin_analyze_document = AsyncMock(return_value=mock_poller)
    
    return mock_client


@pytest.fixture
def mock_translator():
    """Mock Azure Translator client."""
    mock_client = Mock()
    
    # Mock translate response
    mock_client.translate = AsyncMock(return_value=[{
        "translations": [{
            "text": "Hola mundo",
            "to": "es"
        }],
        "detectedLanguage": {
            "language": "en",
            "score": 1.0
        }
    }])
    
    # Mock get_languages
    mock_client.get_languages = AsyncMock(return_value={
        "translation": {
            "en": {"name": "English", "nativeName": "English"},
            "es": {"name": "Spanish", "nativeName": "Español"},
            "fr": {"name": "French", "nativeName": "Français"}
        }
    })
    
    return mock_client


@pytest.fixture
def mock_speech_service():
    """Mock Azure Speech Service client."""
    mock_client = Mock()
    mock_result = Mock()
    
    # Mock transcription result
    mock_result.text = "This is the transcribed text"
    mock_result.reason = "RecognizedSpeech"
    mock_result.properties = {
        "Duration": "30000000",  # 30 seconds in ticks
        "SpeechServiceResponse_JsonResult": '{"NBest":[{"Display":"This is the transcribed text","Confidence":0.95}]}'
    }
    
    # Mock recognize_once_async
    mock_client.recognize_once_async = AsyncMock(return_value=mock_result)
    
    return mock_client


@pytest.fixture
def mock_websocket():
    """Mock WebSocket connection."""
    mock_ws = AsyncMock()
    mock_ws.accept = AsyncMock()
    mock_ws.send_json = AsyncMock()
    mock_ws.receive_json = AsyncMock()
    mock_ws.close = AsyncMock()
    return mock_ws


@pytest.fixture
def job_id():
    """Generate a test job ID."""
    return "test-job-123"


@pytest.fixture
def mock_env_vars(monkeypatch):
    """Set up test environment variables."""
    env_vars = {
        "AZURE_DOC_INTELLIGENCE_ENDPOINT": "https://test-doc.cognitiveservices.azure.com",
        "AZURE_DOC_INTELLIGENCE_KEY": "test-doc-key",
        "AZURE_TRANSLATOR_ENDPOINT": "https://test-translator.cognitiveservices.azure.com",
        "AZURE_TRANSLATOR_KEY": "test-translator-key",
        "AZURE_SPEECH_ENDPOINT": "https://test-speech.cognitiveservices.azure.com",
        "AZURE_SPEECH_KEY": "test-speech-key",
        "AZURE_STORAGE_CONNECTION_STRING": "DefaultEndpointsProtocol=https;AccountName=test;AccountKey=test-key;EndpointSuffix=core.windows.net",
        "AZURE_STORAGE_CONTAINER": "test-container"
    }
    
    for key, value in env_vars.items():
        monkeypatch.setenv(key, value)
    
    return env_vars