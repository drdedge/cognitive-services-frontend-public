# Cognitive Services Frontend

A unified web interface for Azure Cognitive Services including Document Intelligence, Translation, and Transcription services. Built with Vue 3/Tailwind CSS frontend and Python/FastAPI backend.

## Project Overview

This project provides a modern, user-friendly interface for leveraging Azure's powerful AI services. It demonstrates best practices for building scalable web applications with real-time processing capabilities.

### ✅ Core Features
- **Document Intelligence Service** - Extract tables, text, and metadata with confidence scoring
- **Translation Service** - Support for 137 languages with document preservation
- **Transcription Service** - Audio-to-text with speaker diarization
- **Real-time Updates** - WebSocket integration for live progress tracking
- **Modern UI** - Responsive design with Vue 3 and Tailwind CSS
- **RESTful API** - Well-documented FastAPI backend

### 🚀 Roadmap for Enterprise Features
- **Authentication & Authorization** - JWT-based user management system
- **Usage Analytics** - Comprehensive tracking and billing integration
- **Advanced Logging** - ELK stack integration for monitoring
- **Database Integration** - PostgreSQL for persistent data storage

## Features

- 📄 **Document Intelligence**: Extract tables, text, and metadata from PDFs and images
  - Table extraction to CSV/Excel with confidence scoring
  - Text extraction with markdown formatting
  - Confidence analysis dashboard generation
  - Multi-format support (PDF, DOCX, images)
  
- 🌐 **Translation**: Translate documents and text between 137 languages
  - Full Azure Translator API integration
  - Text and document translation
  - Auto-language detection
  - Format preservation for documents
  
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

### Production Deployment

For production deployments, we recommend:

1. **Use Docker Compose Production Configuration**
   ```bash
   docker-compose -f docker-compose.prod.yml up -d
   ```

2. **Security Best Practices**
   - Enable HTTPS/TLS certificates
   - Configure CORS for your specific domains
   - Use Azure Key Vault for credential management
   - Set up monitoring and alerting
   - Implement the authentication system (see roadmap)

3. **Performance Optimization**
   - Use a CDN for frontend assets
   - Enable caching headers
   - Configure auto-scaling for containers
   - Set up health check monitoring

## Color Scheme
The application uses a professional blue-based color scheme:
- Background: `#F5F9FA`
- Header: `#283857`
- Primary Action: `#4F78AB`
- Text: `#3B5781`
- Success: `#28a745`
- Warning: `#ffc107`

## Contributing

We welcome contributions! Please see our contributing guidelines:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## Documentation

- `API_REFERENCE.md` - Complete API documentation
- `IMPLEMENTATION_GUIDE.md` - Guide for implementing enterprise features
- `CLAUDE.md` - Comprehensive technical documentation
- `backend/CLAUDE.md` - Backend implementation details
- `frontend/CLAUDE.md` - Frontend architecture guide

## License

MIT License

Copyright (c) 2024 Cognitive Services Frontend Contributors

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.