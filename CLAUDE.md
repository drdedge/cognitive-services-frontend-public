# Cognitive Services Frontend Project

## Overview
A unified web frontend for Azure Cognitive Services including Document Intelligence, Translation, and Transcription services. Built with Vue 3/Tailwind CSS frontend and Python/FastAPI backend, deployed as a single Docker container.

**Current Status**: ~70% Complete - Translation frontend issue + significant backend refactoring needed

## ⚠️ Important Notes
- Backend has ~40% code duplication requiring refactoring
- Authentication, usage tracking, and comprehensive logging are NOT implemented
- Only Document Intelligence service is truly production-ready
- Translation and Transcription services need refactoring to use base classes

## 🎯 Current Issue: Translation Frontend

### Problem Description
The Translation service backend is fully operational, but the frontend is sending an invalid `source_language` parameter causing 422 errors.

### Technical Details
- **Backend expects**: No `source_language` parameter when auto-detecting
- **Frontend sends**: Empty string or 'auto' as `source_language`
- **Error**: 422 Unprocessable Entity - "Input should be a valid string"

### Quick Fix Verification
```javascript
// In Translation.vue, verify this logic:
if (!sourceLanguage.value || sourceLanguage.value === 'auto') {
  // Should NOT add source_language to request
} else {
  formData.append('source_language', sourceLanguage.value)
}
```

## ✅ What's Working

### Document Intelligence Service (100% Complete)
- Table extraction to CSV/Excel with confidence scoring
- Text extraction with markdown formatting
- Confidence analysis dashboard generation
- Multi-format support (PDF, DOCX, images)
- Real-time progress updates via WebSocket
- Results packaged in organized ZIP structure

### Transcription Service (100% Complete)
- Fast transcription using Azure Speech REST API
- Speaker diarization (up to 20 speakers)
- Smart 1-minute chunking with sentence preservation
- Multiple output formats (TXT, SRT, VTT, JSON)
- Comprehensive speaker analysis reports
- Support for WAV, MP3, OGG, FLAC formats

### Translation Service (Backend 100%, Frontend 95%)
- ✅ Backend: All endpoints operational
- ✅ Backend: 137 languages supported
- ✅ Backend: Document translation with text extraction
- ✅ Backend: Auto-detect language feature
- ❌ Frontend: Source language parameter issue

## Architecture

### Technology Stack
- **Frontend**: Vue 3, Vite, Tailwind CSS
- **Backend**: Python 3.11, FastAPI, Azure SDK
- **Storage**: Azure Blob Storage
- **Real-time**: WebSocket for progress updates
- **Deployment**: Docker, Docker Compose

### Project Structure
```
cognitive-services-frontend/
├── frontend/                    # Vue 3 application
│   ├── src/
│   │   ├── components/         # Reusable UI components
│   │   ├── views/             # Page components
│   │   ├── composables/       # Vue composition utilities
│   │   ├── services/          # API service layer
│   │   └── router/            # Routing configuration
│   └── dist/                  # Production build
├── backend/                    # FastAPI application
│   ├── api/                   # REST endpoints
│   ├── services/              # Business logic
│   │   ├── document_intelligence/
│   │   ├── translation/
│   │   ├── transcription/
│   │   └── storage/
│   ├── models/                # Data models
│   ├── utils/                 # Shared utilities
│   └── tests/                 # Test suite
└── docs/                      # Documentation
```

## API Endpoints

### Document Intelligence
- `POST /api/document-intelligence/process` - Process document
- `POST /api/document-intelligence/estimate-cost` - Estimate cost
- `GET /api/document-intelligence/status/{job_id}` - Job status
- `GET /api/document-intelligence/results/{job_id}` - Download results

### Translation
- `POST /api/translation/translate-text` - Translate text
- `POST /api/translation/translate-document` - Translate document
- `GET /api/translation/languages` - Get 137 supported languages
- `GET /api/translation/status/{job_id}` - Job status
- `GET /api/translation/results/{job_id}` - Download results

### Transcription
- `POST /api/transcription/transcribe` - Start transcription
- `GET /api/transcription/languages` - Get 30 supported languages
- `GET /api/transcription/status/{job_id}` - Job status
- `GET /api/transcription/results/{job_id}` - Download results

### WebSocket
- `WS /ws/{job_id}` - Real-time job updates

## Quick Start

### Prerequisites
- Node.js 18+
- Python 3.11+
- Azure Cognitive Services account
- Azure Storage account

### Environment Setup
Create `.env` file in backend directory:
```bash
# Azure Services
AZURE_DOC_INTELLIGENCE_ENDPOINT=https://your-endpoint.cognitiveservices.azure.com/
AZURE_DOC_INTELLIGENCE_KEY=your-key
AZURE_TRANSLATOR_ENDPOINT=https://api.cognitive.microsofttranslator.com/
AZURE_TRANSLATOR_KEY=your-key
AZURE_TRANSLATOR_REGION=your-region
AZURE_SPEECH_ENDPOINT=https://your-region.api.cognitive.microsoft.com/
AZURE_SPEECH_KEY=your-key

# Storage
AZURE_STORAGE_CONNECTION_STRING=your-connection-string
AZURE_STORAGE_CONTAINER=cognitive-services
```

### Development
```bash
# Terminal 1: Start Backend
cd backend
pip install -r requirements.txt
python main.py  # Runs on http://localhost:8000

# Terminal 2: Start Frontend
cd frontend
npm install
npm run dev     # Runs on http://localhost:3000
```

### Production Build
```bash
# Build frontend
cd frontend
npm run build

# Build Docker image
docker build -t cognitive-services-app .
docker run -p 80:80 --env-file .env cognitive-services-app
```

## Key Features

### Real-time Processing
- WebSocket connections for live updates
- Progress tracking with detailed stages
- Automatic reconnection on connection loss

### File Processing Pipeline
```
Upload → Validate → Create Job → Process (Azure) → Package Results → Download
           │            │             │                  │
           └────────────┴─────────────┴──────────────────┴─→ WebSocket Updates
```

### Result Packaging
All services package results in organized ZIP files:
```
results.zip
├── original/           # Original input files
├── processed/          # Processed outputs
├── metadata/           # Processing statistics
└── summary.json        # Job summary
```

## Development Guidelines

### Frontend Patterns
```javascript
// Service integration pattern
const { processDocument } = useDocumentIntelligence()
const { isConnected, subscribe } = useWebSocket()

// Error handling pattern
try {
  const result = await processDocument(file, options)
  // Handle success
} catch (error) {
  notify.error(error.message)
}
```

### Backend Patterns
```python
# Async processing pattern
@router.post("/process")
async def process(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...)
):
    job_id = await job_manager.create_job(...)
    background_tasks.add_task(process_task, job_id)
    return {"job_id": job_id}

# WebSocket updates
await websocket_manager.broadcast_job_update(
    job_id,
    {"progress": 50, "message": "Processing..."}
)
```

## Testing

### Backend Tests
```bash
cd backend
pytest                          # Run all tests
pytest tests/test_translation_docx.py  # Test specific service
pytest --cov=.                  # With coverage
```

### Frontend Tests
```bash
cd frontend
npm test                        # Run tests (when implemented)
```

## Performance Considerations

### Optimizations Implemented
- Connection pooling for Azure clients
- Streaming for large file uploads
- Async processing for all I/O operations
- Progress update throttling (max 1/second)
- Efficient file chunking for large documents

### Resource Limits
- Max file size: 50MB (configurable)
- Max audio duration: 2 hours
- Max concurrent jobs: 10 per user
- WebSocket connections: 50 concurrent

## Security

### Implemented Measures
- CORS configuration for frontend origin
- File type validation and sanitization
- Size limits and rate limiting
- Secure file storage with cleanup
- Input validation at all endpoints

### Production Considerations
- Enable HTTPS/TLS
- Implement authentication
- Add API rate limiting
- Enable audit logging
- Regular security updates

## Troubleshooting

### Translation Frontend Issue
If translation fails with 422 error:
1. Clear browser cache
2. Check Network tab for request payload
3. Verify `source_language` is not sent when empty
4. Check console for JavaScript errors
5. Ensure latest frontend code is loaded

### Common Issues
- **WebSocket disconnects**: Check CORS and firewall settings
- **File upload fails**: Verify file size and type limits
- **Azure errors**: Check API keys and endpoints
- **Processing hangs**: Review backend logs for errors

## Project Status Summary

| Service | Backend | Frontend | Integration | Actual Status |
|---------|---------|----------|-------------|---------|
| Document Intelligence | ✅ 100% | ✅ 100% | ✅ 100% | **PRODUCTION READY** |
| Transcription | ⚠️ 80% | ✅ 100% | ⚠️ 90% | **NEEDS REFACTORING** |
| Translation | ⚠️ 80% | ❌ 95% | ❌ 85% | **FRONTEND FIX + REFACTORING** |
| Storage | ✅ 100% | N/A | ✅ 100% | **PRODUCTION READY** |
| WebSocket | ⚠️ 90% | ✅ 100% | ⚠️ 95% | **NEEDS REFACTORING** |
| Authentication | ❌ 0% | ❌ 0% | ❌ 0% | **NOT IMPLEMENTED** |
| Usage Tracking | ❌ 0% | ❌ 0% | ❌ 0% | **NOT IMPLEMENTED** |
| Logging System | ⚠️ 20% | ❌ 0% | ❌ 10% | **BASIC ONLY** |

**Overall Completion: ~70%** - Translation frontend issue + backend refactoring + missing core features

## 📋 Outstanding Features (Not Implemented)

### 1. Authentication & Authorization
- **Current State**: No authentication system exists
- **Impact**: All endpoints are publicly accessible
- **Required Implementation**:
  - JWT token-based authentication
  - User registration and login endpoints
  - Role-based access control (RBAC)
  - Session management
  - API key management for service access
  - OAuth2/Azure AD integration

### 2. Usage Tracking & Billing
- **Current State**: No persistent usage tracking
- **Impact**: Cannot track costs or usage patterns
- **Required Implementation**:
  - Database schema for usage data
  - Real-time usage collection
  - Cost aggregation by user/service
  - Usage quotas and limits
  - Billing integration
  - Usage analytics dashboard

### 3. Comprehensive Logging
- **Current State**: Basic console logging only
- **Impact**: No audit trail or debugging capabilities
- **Required Implementation**:
  - Structured logging with correlation IDs
  - Log aggregation (ELK stack or similar)
  - Performance metrics collection
  - Error tracking and alerting
  - Audit logging for compliance
  - Log retention policies

### 4. Backend Refactoring (In Progress)
- **Current State**: ~40% code duplication across services
- **Impact**: Difficult to maintain and extend
- **Required Implementation**:
  - Base service classes (Phase 1 partially complete)
  - Shared utilities consolidation
  - Standardized API patterns
  - Common error handling
  - Unified testing framework