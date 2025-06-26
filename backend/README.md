# Azure Cognitive Services Backend

A high-performance FastAPI backend that provides unified access to Azure Cognitive Services including Document Intelligence, Translation, and Speech Services. Features real-time WebSocket communication, robust file management, and enterprise-grade security.

## Table of Contents
- [Overview](#overview)
- [Architecture](#architecture)
- [Quick Start](#quick-start)
- [API Documentation](#api-documentation)
- [Service Implementations](#service-implementations)
- [Development](#development)
- [Testing](#testing)
- [Deployment](#deployment)
- [Troubleshooting](#troubleshooting)

## Overview

### Features
- **Document Intelligence**: Extract tables, text, and metadata from documents with confidence scoring
- **Translation Service**: Translate text and documents between languages while preserving formatting
- **Transcription Service**: Convert audio to text with speaker diarization and multiple output formats
- **Real-time Updates**: WebSocket connections for live progress tracking
- **Secure File Handling**: Azure Blob Storage integration with automatic cleanup
- **Job Management**: Async processing with queue management and status tracking
- **Production Ready**: Comprehensive error handling, logging, and monitoring

### Current Status
- ✅ **Document Intelligence**: Fully operational with Azure integration
- 🚧 **Translation**: Infrastructure complete, awaiting Azure SDK integration
- 🚧 **Transcription**: Infrastructure complete, awaiting Azure SDK integration
- ✅ **Storage & WebSocket**: Production ready

## Architecture

### System Architecture
```
┌─────────────────────────────────────────────────────────────────────┐
│                         FastAPI Application                          │
├─────────────────────────────────────────────────────────────────────┤
│  ┌─────────────┐    ┌──────────────┐    ┌──────────────────────┐  │
│  │ API Layer   │───▶│ Service Layer│───▶│ Azure Integration    │  │
│  │             │    │              │    │                      │  │
│  │ • Endpoints │    │ • Business   │    │ • Document Intel     │  │
│  │ • WebSocket │    │   Logic      │    │ • Translator         │  │
│  │ • Validation│    │ • Processing │    │ • Speech Services    │  │
│  └─────────────┘    └──────────────┘    └──────────────────────┘  │
│         │                   │                      │                │
│         └───────────────────┴──────────────────────┴────────┐      │
│                                                             ▼      │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │                    Infrastructure Layer                       │  │
│  │                                                               │  │
│  │  • Job Management    • File Handling    • WebSocket Manager  │  │
│  │  • Azure Clients     • Error Handling   • Logging           │  │
│  │  • Configuration     • Security         • Monitoring        │  │
│  └──────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────┘
```

### Directory Structure
```
backend/
├── api/                    # API endpoints
│   ├── document_intelligence.py
│   ├── translation.py
│   ├── transcription.py
│   └── storage.py
├── services/               # Business logic
│   ├── document_intelligence/
│   │   ├── service.py
│   │   ├── processor.py
│   │   ├── table_extractor.py
│   │   └── confidence_dashboard.py
│   ├── translation/
│   ├── transcription/
│   ├── storage/
│   ├── websocket/
│   └── shared/
├── models/                 # Data models
│   ├── base.py
│   ├── document_models.py
│   ├── translation_models.py
│   └── transcription_models.py
├── utils/                  # Utilities
│   ├── azure_clients.py
│   ├── file_handler.py
│   ├── job_manager.py
│   └── config.py
├── tests/                  # Test suite
│   ├── conftest.py
│   ├── fixtures/
│   └── test_*.py
├── main.py                # Application entry
├── requirements.txt       # Dependencies
└── Dockerfile            # Container config
```

## Quick Start

### Prerequisites
- Python 3.11+
- Azure Cognitive Services subscriptions
- Azure Storage Account
- Docker (optional)

### Installation

1. **Clone and navigate to backend**
```bash
cd cognitive-services-frontend/backend
```

2. **Create virtual environment**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Configure environment variables**
```bash
cp .env.example .env
# Edit .env with your Azure credentials
```

5. **Run the application**
```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

### Environment Variables
```bash
# Azure Cognitive Services
AZURE_DOC_INTELLIGENCE_ENDPOINT=https://your-doc-intelligence.cognitiveservices.azure.com
AZURE_DOC_INTELLIGENCE_KEY=your-doc-intelligence-key
AZURE_TRANSLATOR_ENDPOINT=https://your-translator.cognitiveservices.azure.com
AZURE_TRANSLATOR_KEY=your-translator-key
AZURE_SPEECH_ENDPOINT=https://your-speech.cognitiveservices.azure.com
AZURE_SPEECH_KEY=your-speech-key

# Azure Storage
AZURE_STORAGE_CONNECTION_STRING=DefaultEndpointsProtocol=https;AccountName=...
AZURE_STORAGE_CONTAINER=cognitive-services

# Application Settings
CORS_ORIGINS=http://localhost:3000,https://your-frontend.com
MAX_UPLOAD_SIZE_MB=50
JWT_SECRET_KEY=your-secret-key
API_RATE_LIMIT=100
```

## API Documentation

### Interactive Documentation
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### Core Endpoints

#### Document Intelligence
```http
POST /api/document-intelligence/process
Content-Type: multipart/form-data

Request:
- file: binary (required)
- analysis_type: string (default: "layout")
- extract_tables: boolean (default: true)
- include_confidence: boolean (default: true)

Response:
{
  "job_id": "uuid",
  "status": "processing",
  "created_at": "2025-06-16T10:00:00Z"
}
```

```http
GET /api/document-intelligence/results/{job_id}

Response: ZIP file containing:
- analysis_summary.json
- confidence_dashboard.png
- document_tables.xlsx
- document.md
- csv/*.csv (individual tables)
- md/md_pages/*.md (page content)
```

#### Translation
```http
POST /api/translation/translate-text
Content-Type: application/json

Request:
{
  "text": "Hello world",
  "source_language": "en",
  "target_language": "es"
}

Response:
{
  "translated_text": "Hola mundo",
  "detected_language": "en",
  "confidence": 0.98
}
```

#### WebSocket
```javascript
// Connect to WebSocket for real-time updates
const ws = new WebSocket('ws://localhost:8000/ws/{job_id}');

ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  console.log('Progress:', data.progress);
  console.log('Status:', data.status);
};
```

### Error Responses
```json
{
  "error": {
    "code": "INVALID_FILE_FORMAT",
    "message": "File format not supported",
    "details": {
      "supported_formats": [".pdf", ".docx", ".png", ".jpg"]
    }
  }
}
```

## Service Implementations

### Document Intelligence Service (✅ Fully Operational)

#### Features
- Extract tables to CSV/Excel with confidence scoring
- Convert documents to structured markdown
- Generate confidence visualization dashboards
- Support for PDF, DOCX, and image formats
- Real-time progress tracking via WebSocket

#### Processing Flow
```
1. File Upload → Validation → Azure Blob Storage
2. Create Job → Queue Processing → WebSocket Updates
3. Azure API → Extract Content → Process Results
4. Package Results → Create ZIP → Upload to Blob
5. Return Download URL → Complete Job
```

#### Result Package Structure
```
results.zip
├── analysis_summary.json      # Processing statistics
├── confidence_dashboard.png   # Visual quality metrics
├── document_tables.xlsx       # All tables in Excel
├── document.md               # Full document markdown
├── azure_response.json       # Raw API response
├── csv/                      # Individual table CSVs
└── md/md_pages/             # Individual page markdown
```

### Translation Service (🚧 Infrastructure Ready)

#### Planned Features
- Text and document translation
- Language auto-detection
- Batch translation support
- Format preservation for documents
- Support for 100+ languages

### Transcription Service (🚧 Infrastructure Ready)

#### Planned Features
- Audio to text conversion
- Speaker diarization
- Multiple output formats (TXT, SRT, VTT, JSON)
- Support for various audio formats
- Real-time transcription updates

## Development

### Development Setup

1. **Install development dependencies**
```bash
pip install -r requirements-dev.txt
```

2. **Run with auto-reload**
```bash
uvicorn main:app --reload --log-level debug
```

3. **Code formatting**
```bash
black .
isort .
flake8 .
```

### Adding New Features

#### 1. Create Service Implementation
```python
# services/new_service/service.py
class NewService:
    def __init__(self):
        self.client = self._initialize_client()
    
    async def process(self, data):
        # Implementation
        pass
```

#### 2. Define Models
```python
# models/new_models.py
from pydantic import BaseModel

class NewRequest(BaseModel):
    field1: str
    field2: int

class NewResponse(BaseModel):
    result: str
    status: str
```

#### 3. Create API Endpoints
```python
# api/new_endpoints.py
from fastapi import APIRouter

router = APIRouter(prefix="/api/new-service")

@router.post("/process")
async def process(request: NewRequest):
    # Implementation
    pass
```

#### 4. Add Tests
```python
# tests/test_new_service.py
async def test_new_service_process():
    # Test implementation
    pass
```

### Code Standards
- Use type hints for all function parameters and returns
- Follow PEP 8 style guide
- Write docstrings for all classes and public methods
- Implement comprehensive error handling
- Add logging for debugging
- Write unit tests for new features

## Testing

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=. --cov-report=html

# Run specific test file
pytest tests/test_document_intelligence.py

# Run tests by marker
pytest -m unit          # Unit tests only
pytest -m integration   # Integration tests
pytest -m azure        # Azure service tests
```

### Test Categories
- **Unit Tests**: Test individual components in isolation
- **Integration Tests**: Test service interactions
- **API Tests**: Test endpoint functionality
- **WebSocket Tests**: Test real-time communication
- **Performance Tests**: Test system under load

### Test Infrastructure
- Comprehensive Azure service mocks
- Sample test data for all file types
- WebSocket testing utilities
- Performance benchmarking tools

## Deployment

### Docker Deployment

1. **Build image**
```bash
docker build -t cognitive-services-backend .
```

2. **Run container**
```bash
docker run -p 8000:8000 --env-file .env cognitive-services-backend
```

### Docker Compose
```yaml
version: '3.8'
services:
  backend:
    build: ./backend
    ports:
      - "8000:8000"
    environment:
      - AZURE_DOC_INTELLIGENCE_ENDPOINT=${AZURE_DOC_INTELLIGENCE_ENDPOINT}
      - AZURE_DOC_INTELLIGENCE_KEY=${AZURE_DOC_INTELLIGENCE_KEY}
      # ... other environment variables
    volumes:
      - ./backend:/app
```

### Production Considerations
- Use environment-specific configurations
- Enable HTTPS with SSL certificates
- Configure rate limiting and security headers
- Set up monitoring and alerting
- Implement log aggregation
- Configure auto-scaling policies
- Set up database for persistent job storage
- Implement Redis for caching and queuing

### Health Monitoring
```http
GET /health

Response:
{
  "status": "healthy",
  "timestamp": "2025-06-16T10:00:00Z",
  "services": {
    "storage": "healthy",
    "document_intelligence": "healthy",
    "translation": "healthy",
    "transcription": "healthy"
  }
}
```

## Troubleshooting

### Common Issues

#### 1. Azure Connection Errors
```python
# Check Azure credentials
AZURE_DOC_INTELLIGENCE_ENDPOINT=https://...
AZURE_DOC_INTELLIGENCE_KEY=...

# Verify network connectivity to Azure
curl https://your-endpoint.cognitiveservices.azure.com
```

#### 2. File Upload Issues
- Check file size limits (default: 50MB)
- Verify supported file formats
- Ensure proper CORS configuration
- Check storage permissions

#### 3. WebSocket Connection Issues
- Verify WebSocket URL format: `ws://host:port/ws/{job_id}`
- Check firewall/proxy settings
- Ensure frontend and backend are on same network
- Verify CORS allows WebSocket connections

#### 4. Memory/Performance Issues
- Monitor memory usage during processing
- Implement file streaming for large files
- Use connection pooling for Azure clients
- Enable response caching where appropriate

### Debug Mode
```bash
# Enable debug logging
export LOG_LEVEL=DEBUG
uvicorn main:app --log-level debug

# View detailed error messages
export SHOW_ERROR_DETAILS=true
```

### Logging
```python
# Application logs location
./logs/app.log

# Log format
{
  "timestamp": "2025-06-16T10:00:00Z",
  "level": "INFO",
  "logger": "backend.services.document_intelligence",
  "message": "Processing started",
  "job_id": "uuid",
  "correlation_id": "uuid"
}
```

## Contributing

1. Check `TODO.md` for current development priorities
2. Follow the established code patterns
3. Write tests for new features
4. Update documentation
5. Submit PR with clear description

## License

This project is part of the Cognitive Services Frontend application.

## Support

For issues and questions:
1. Check the troubleshooting section
2. Review test cases for examples
3. Check Azure service documentation
4. Review API documentation at `/docs`