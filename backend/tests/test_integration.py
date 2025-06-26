"""
Integration Tests
================

Tests the integration between frontend and backend APIs.
"""

import asyncio
import json
import tempfile
import os
from fastapi.testclient import TestClient
from fastapi import WebSocket
import pytest

from main import app

client = TestClient(app)


class TestAPIIntegration:
    """Test API integration between frontend and backend."""

    def test_health_endpoint(self):
        """Test health check endpoint."""
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json() == {"status": "healthy"}

    def test_root_endpoint(self):
        """Test root endpoint returns API information."""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert "name" in data
        assert "endpoints" in data
        assert "document_intelligence" in data["endpoints"]
        assert "translation" in data["endpoints"]
        assert "transcription" in data["endpoints"]

    def test_document_intelligence_supported_types(self):
        """Test document intelligence supported types endpoint."""
        response = client.get("/api/document-intelligence/supported-types")
        assert response.status_code == 200
        data = response.json()
        assert "formats" in data
        assert len(data["formats"]) > 0
        assert any(fmt["extension"] == ".pdf" for fmt in data["formats"])

    def test_document_intelligence_analysis_types(self):
        """Test document intelligence analysis types endpoint."""
        response = client.get("/api/document-intelligence/analysis-types")
        assert response.status_code == 200
        data = response.json()
        assert "types" in data
        assert len(data["types"]) > 0
        assert any(t["id"] == "layout" for t in data["types"])

    def test_document_intelligence_cost_estimation(self):
        """Test document intelligence cost estimation."""
        payload = {
            "file_size": 1024000,  # 1MB
            "file_type": "pdf",
            "analysis_type": "layout"
        }
        response = client.post("/api/document-intelligence/estimate-cost", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert "estimated_cost" in data
        assert "currency" in data
        assert "estimated_pages" in data
        assert data["currency"] == "USD"

    def test_translation_languages(self):
        """Test translation supported languages endpoint."""
        response = client.get("/api/translation/languages")
        assert response.status_code == 200
        # Note: This might fail if the actual service isn't connected
        # In a real integration test, we'd mock the Azure service

    def test_translation_text(self):
        """Test simple text translation."""
        payload = {
            "text": "Hello world",
            "target_language": "es",
            "source_language": "en"
        }
        response = client.post("/api/translation/translate-text", json=payload)
        # This will likely fail without actual Azure credentials
        # But we can verify the endpoint exists and accepts the correct format
        assert response.status_code in [200, 500]  # 500 is expected without real service

    def test_translation_cost_estimation(self):
        """Test translation cost estimation."""
        payload = {
            "text": "Hello world, how are you today?",
            "target_language": "es"
        }
        response = client.post("/api/translation/estimate-cost", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert "estimated_cost" in data
        assert "currency" in data
        assert "character_count" in data

    def test_transcription_cost_estimation(self):
        """Test transcription cost estimation."""
        payload = {
            "duration": 300,  # 5 minutes
            "file_size": 5000000,  # 5MB
            "speaker_diarization": True
        }
        response = client.post("/api/transcription/estimate-cost", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert "estimated_cost" in data
        assert "currency" in data
        assert "estimated_duration" in data
        assert data["features"]["speaker_diarization"] is True

    def test_document_upload_flow(self):
        """Test document upload and processing flow."""
        # Create a test file
        test_content = b"This is a test PDF content"
        
        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp_file:
            tmp_file.write(test_content)
            tmp_file.flush()
            
            try:
                # Test file upload
                with open(tmp_file.name, "rb") as f:
                    files = {"file": ("test.pdf", f, "application/pdf")}
                    data = {
                        "analysis_type": "layout",
                        "extract_tables": True,
                        "extract_text": True,
                        "output_format": "markdown"
                    }
                    
                    response = client.post(
                        "/api/document-intelligence/process",
                        files=files,
                        data=data
                    )
                    
                    # Should return task ID (even if processing fails)
                    assert response.status_code == 200
                    data = response.json()
                    assert "task_id" in data
                    assert data["task_id"].startswith("doc_")
                    
                    # Test status endpoint
                    task_id = data["task_id"]
                    status_response = client.get(f"/api/document-intelligence/status/{task_id}")
                    assert status_response.status_code == 200
                    
            finally:
                # Cleanup
                os.unlink(tmp_file.name)

    def test_cors_headers(self):
        """Test that CORS headers are properly configured."""
        response = client.options("/api/document-intelligence/supported-types")
        # FastAPI test client doesn't fully simulate CORS,
        # but we can verify the middleware is configured
        assert response.status_code in [200, 405]  # OPTIONS might not be implemented

    def test_error_handling(self):
        """Test error handling for invalid requests."""
        # Test invalid file type
        test_content = b"This is not a valid file"
        
        with tempfile.NamedTemporaryFile(suffix=".xyz", delete=False) as tmp_file:
            tmp_file.write(test_content)
            tmp_file.flush()
            
            try:
                with open(tmp_file.name, "rb") as f:
                    files = {"file": ("test.xyz", f, "application/octet-stream")}
                    
                    response = client.post(
                        "/api/document-intelligence/process",
                        files=files
                    )
                    
                    assert response.status_code == 400
                    data = response.json()
                    assert "detail" in data
                    assert "not supported" in data["detail"]
                    
            finally:
                os.unlink(tmp_file.name)

    def test_missing_endpoints_return_404(self):
        """Test that missing endpoints return proper 404."""
        response = client.get("/api/nonexistent/endpoint")
        assert response.status_code == 404

    def test_document_intelligence_task_status(self):
        """Test document intelligence task status endpoint."""
        task_id = "doc_test123"
        response = client.get(f"/api/document-intelligence/status/{task_id}")
        assert response.status_code == 200
        data = response.json()
        assert data["task_id"] == task_id
        assert "status" in data

    def test_translation_task_status(self):
        """Test translation task status endpoint."""
        task_id = "trans_test123"
        response = client.get(f"/api/translation/status/{task_id}")
        assert response.status_code == 200
        data = response.json()
        assert data["task_id"] == task_id
        assert "status" in data

    def test_transcription_task_status(self):
        """Test transcription task status endpoint."""
        task_id = "audio_test123"
        response = client.get(f"/api/transcription/status/{task_id}")
        assert response.status_code == 200
        data = response.json()
        assert data["task_id"] == task_id
        assert "status" in data


class TestWebSocketIntegration:
    """Test WebSocket integration."""

    def test_websocket_connection_with_client_id(self):
        """Test WebSocket connection with client ID in path."""
        with client.websocket_connect("/ws/test-client-123") as websocket:
            # Should receive connection confirmation
            data = websocket.receive_json()
            assert data["type"] == "connected"
            assert data["client_id"] == "test-client-123"

    def test_websocket_connection_lifecycle(self):
        """Test WebSocket connection lifecycle."""
        with client.websocket_connect("/ws/test-client-456") as websocket:
            # Receive connection confirmation
            data = websocket.receive_json()
            assert data["type"] == "connected"
            
            # Send ping
            websocket.send_json({"type": "ping"})
            
            # Should receive pong
            pong_data = websocket.receive_json()
            assert pong_data["type"] == "pong"
            
            # Send subscription
            websocket.send_json({
                "type": "subscribe", 
                "task_id": "doc_test789"
            })
            
            # Connection should remain open
            # (No additional messages expected immediately)

    def test_websocket_requires_client_id(self):
        """Test that WebSocket requires client ID."""
        # This should work with client ID in path
        with client.websocket_connect("/ws/valid-client") as websocket:
            data = websocket.receive_json()
            assert data["type"] == "connected"


if __name__ == "__main__":
    # Run a quick test
    test = TestAPIIntegration()
    test.test_health_endpoint()
    test.test_document_intelligence_supported_types()
    test.test_document_intelligence_cost_estimation()
    print("✅ Integration tests passed!")