# Cognitive Services Frontend

A unified web interface for Azure Cognitive Services including Document Intelligence, Translation, and Transcription services. Built with Vue 3/Tailwind CSS frontend and Python/FastAPI backend.

## 🚧 Project Status: ~70% Complete

### ✅ What's Working
- **Document Intelligence Service** - Fully operational with table extraction, text analysis, and confidence scoring
- **Frontend UI** - Complete responsive interface with real-time WebSocket updates
- **Core Infrastructure** - File processing, job management, and result packaging

### ⚠️ Known Issues
1. **Translation Frontend Bug** - Service sends invalid `source_language` parameter causing 422 errors
2. **Backend Refactoring Needed** - ~40% code duplication across services
3. **Missing Core Features** - No authentication, usage tracking, or comprehensive logging

### 📋 Outstanding Features (Not Implemented)
- **Authentication & Authorization** - All endpoints are currently public
- **Usage Tracking & Billing** - No persistent usage or cost tracking
- **Comprehensive Logging** - Only basic console logging exists
- **Database Integration** - No data persistence beyond job processing

## Features

### Implemented
- 📄 **Document Intelligence**: Extract tables, text, and metadata from PDFs and images
  - Table extraction to CSV/Excel with confidence scoring
  - Text extraction with markdown formatting
  - Confidence analysis dashboard generation
  - Multi-format support (PDF, DOCX, images)
  
- 🌐 **Translation**: Translate documents and text between 137 languages
  - Backend fully operational with Azure Translator API
  - Text and document translation
  - Auto-language detection
  - ⚠️ Frontend has parameter bug preventing usage
  
- 🎤 **Transcription**: Convert audio to text with speaker identification
  - Fast transcription using Azure Speech REST API
  - Speaker diarization (up to 20 speakers)
  - Multiple output formats (TXT, SRT, VTT, JSON)
  - Support for WAV, MP3, OGG, FLAC formats

## Quick Start

### Prerequisites
- Node.js 18+ and npm
- Python 3.11+
- Azure Cognitive Services subscriptions:
  - Document Intelligence
  - Translator
  - Speech Services
- Azure Storage account
- Docker and Docker Compose (for containerized deployment)

### Environment Configuration

1. Copy the example environment file:
```bash
cp backend/.env.example backend/.env
```

2. Configure all required Azure credentials in `.env`:
```env
# Azure Services
AZURE_DOC_INTELLIGENCE_ENDPOINT=https://your-endpoint.cognitiveservices.azure.com/
AZURE_DOC_INTELLIGENCE_KEY=your-key
AZURE_TRANSLATOR_ENDPOINT=https://api.cognitive.microsofttranslator.com/
AZURE_TRANSLATOR_KEY=your-key
AZURE_TRANSLATOR_REGION=your-region
AZURE_SPEECH_KEY=your-key
AZURE_SPEECH_REGION=your-region

# Storage
AZURE_STORAGE_CONNECTION_STRING=your-connection-string
AZURE_STORAGE_CONTAINER_NAME=cognitive-services
```

### Development Setup

#### Option 1: Direct Execution
```bash
# Terminal 1: Backend
cd backend
pip install -r requirements.txt
python main.py  # Runs on http://localhost:8000

# Terminal 2: Frontend
cd frontend
npm install
npm run dev     # Runs on http://localhost:3000
```

#### Option 2: Docker Compose (Recommended)
```bash
# Build and start all services
docker-compose up --build

# Access:
# - Frontend: http://localhost:3000
# - Backend API: http://localhost:8000
# - API Documentation: http://localhost:8000/docs
```

### Windows Users - Known Issue
If you encounter `Cannot find module @rollup/rollup-win32-x64-msvc`:
```bash
cd frontend
npm install @rollup/rollup-win32-x64-msvc
npm run dev
```

## Architecture

### Technology Stack

#### Frontend
- **Vue 3** - Progressive JavaScript framework
- **Vite** - Next generation frontend tooling
- **Tailwind CSS** - Utility-first CSS framework
- **Pinia** - State management
- **Vue Router** - Client-side routing
- **Axios** - HTTP client with retry logic

#### Backend
- **FastAPI** - Modern Python web framework
- **Azure SDK** - Cognitive Services integration
- **WebSockets** - Real-time progress updates
- **Pydantic** - Data validation
- **pytest** - Comprehensive test suite

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

## API Documentation

### REST Endpoints

#### Document Intelligence
- `POST /api/document-intelligence/process` - Process document
- `POST /api/document-intelligence/estimate-cost` - Estimate processing cost
- `GET /api/document-intelligence/status/{job_id}` - Get job status
- `GET /api/document-intelligence/results/{job_id}` - Download results

#### Translation
- `POST /api/translation/translate-text` - Translate text
- `POST /api/translation/translate-document` - Translate document
- `GET /api/translation/languages` - Get supported languages
- `GET /api/translation/status/{job_id}` - Get job status
- `GET /api/translation/results/{job_id}` - Download results

#### Transcription
- `POST /api/transcription/transcribe` - Start transcription
- `GET /api/transcription/languages` - Get supported languages
- `GET /api/transcription/status/{job_id}` - Get job status
- `GET /api/transcription/results/{job_id}` - Download results

### WebSocket
- `WS /ws/{job_id}` - Real-time job updates

Full API documentation available at: http://localhost:8000/docs

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

## Deployment

### Production Build

#### Frontend
```bash
cd frontend
npm run build
```

#### Docker Deployment
```bash
# Build production image
docker build -t cognitive-services-app .

# Run with environment file
docker run -p 80:80 --env-file backend/.env cognitive-services-app
```

### Security Considerations
⚠️ **WARNING: No authentication is currently implemented!**

Before deploying to production:
1. Implement authentication and authorization
2. Enable HTTPS/TLS
3. Configure CORS for specific domains only
4. Implement rate limiting
5. Use Azure Key Vault for secrets
6. Enable comprehensive logging
7. Set up monitoring and alerting

## Color Scheme
The application uses a professional blue-based color scheme:
- Background: `#F5F9FA`
- Header: `#283857`
- Primary Action: `#4F78AB`
- Text: `#3B5781`
- Success: `#28a745`
- Warning: `#ffc107`

## Contributing

1. Check `CLAUDE.md` for detailed technical documentation
2. Review `backend/TODO.md` for pending tasks
3. Fix the translation frontend parameter issue (Priority #1)
4. Help with backend refactoring to reduce code duplication
5. Implement missing features (auth, logging, usage tracking)

## Documentation
- `CLAUDE.md` - Comprehensive technical documentation
- `backend/CLAUDE.md` - Backend implementation details
- `frontend/CLAUDE.md` - Frontend architecture guide
- `backend/TODO.md` - Consolidated task tracking

## License
[Your License Here]