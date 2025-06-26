# Backend Development Guide

## Overview
FastAPI-based backend service providing REST APIs and WebSocket connections for Azure Cognitive Services integration. This guide provides detailed implementation patterns, architecture decisions, and development guidelines for the backend system.

## Documentation Structure
- **README.md**: User-facing documentation with setup instructions and API reference
- **CLAUDE.md**: This file - detailed development guide and implementation patterns
- **TODO.md**: Consolidated task tracking and development priorities

## Recent Updates

### 2025-06-22 - Backend Refactoring Plan
- Added comprehensive refactoring plan to address ~40% code duplication
- Identified duplicate patterns across all three services
- Designed base class architecture for consistency
- Created 5-phase implementation roadmap
- Added progress tracking and maintenance guidelines

### 2025-06-16 - Initial Implementation
- Fixed UUID prefix issue in ZIP file generation - filenames now match original names
- Consolidated all backend TODO.md files into single /backend/TODO.md
- Removed redundant backup files and Python cache directories
- Updated .gitignore to prevent cache files in version control
- Implemented Transcription Service using Azure Speech Services fast transcription API
  - REST API implementation with aiohttp (no SDK dependency)
  - Speaker diarization with up to 20 speakers
  - 1-minute chunk formatting with complete sentences
  - Multiple output formats (TXT, SRT, VTT, JSON)
  - Comprehensive speaker analysis reports

## Architecture

### Service Architecture Diagram
```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              FastAPI Application                             │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  main.py                                                                    │
│  ├── App initialization                                                     │
│  ├── Middleware setup (CORS, Error handling)                              │
│  ├── Route registration                                                     │
│  └── WebSocket endpoint                                                     │
│                                                                             │
├─────────────────────────────────────────────────────────────────────────────┤
│                           API Layer (/api/)                                  │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌─────────────────────┐  ┌─────────────────────┐  ┌─────────────────────┐│
│  │ document_intelligence│  │    translation      │  │   transcription     ││
│  │                     │  │                     │  │                     ││
│  │ • /process          │  │ • /translate-text   │  │ • /transcribe       ││
│  │ • /estimate-cost    │  │ • /translate-doc    │  │ • /estimate-cost    ││
│  │ • /status/{id}      │  │ • /estimate-cost    │  │ • /status/{id}      ││
│  │ • /results/{id}     │  │ • /languages        │  │ • /results/{id}     ││
│  └──────────┬──────────┘  └──────────┬──────────┘  └──────────┬──────────┘│
│             │                        │                         │            │
├─────────────────┴────────────────────┴─────────────────────────┴────────────┤
│                         Service Layer (/services/)                           │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌───────────────────────────────────────────────────────────────────────┐ │
│  │              document_intelligence/ (✅ Fully Operational)             │ │
│  ├───────────────────────────────────────────────────────────────────────┤ │
│  │ • service.py - DocumentIntelligenceService                             │ │
│  │   ├── analyze_document() - Main processing method                      │ │
│  │   └── create_results_package() - ZIP packaging                        │ │
│  │ • processor.py - Document processing logic                             │ │
│  │   ├── extract_text_content() - Text & markdown extraction             │ │
│  │   └── calculate_confidence_statistics() - Quality metrics             │ │
│  │ • table_extractor.py - Table processing                               │ │
│  │   ├── process_tables() - Extract tables from document                 │ │
│  │   └── create_excel_from_tables() - Generate Excel file               │ │
│  │ • confidence_dashboard.py - Visualization                              │ │
│  │   └── create_confidence_dashboard() - Generate confidence charts      │ │
│  └───────────────────────────────────────────────────────────────────────┘ │
│                                                                             │
│  ┌───────────────────────────────────────────────────────────────────────┐ │
│  │   translation/, transcription/, storage/, websocket/ (Mixed Status)    │ │
│  │   └── service.py/manager.py - Service implementations                  │ │
│  └───────────────────────────────────────────────────────────────────────┘ │
│                                                                             │
│  ┌───────────────────────────────────────────────────────────────────────┐ │
│  │                    shared/ - Common Utilities                          │ │
│  │   └── field_accessor.py - Universal field access helper               │ │
│  └───────────────────────────────────────────────────────────────────────┘ │
│                                                                             │
├─────────────────────────────────────────────────────────────────────────────┤
│                          Utility Layer (/utils/)                             │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌─────────────────────┐  ┌─────────────────────┐  ┌─────────────────────┐│
│  │   azure_clients.py  │  │   file_handler.py   │  │   job_manager.py    ││
│  │                     │  │                     │  │                     ││
│  │ • get_doc_intel()   │  │ • create_temp_file()│  │ • create_job()      ││
│  │ • get_translator()  │  │ • zip_files()       │  │ • update_status()   ││
│  │ • get_speech()      │  │ • upload_to_blob()  │  │ • get_job()         ││
│  │ • health_check()    │  │ • download_file()   │  │ • broadcast_update()││
│  └─────────────────────┘  └─────────────────────┘  └─────────────────────┘│
│                                                                             │
│  ┌─────────────────────┐  ┌─────────────────────┐  ┌─────────────────────┐│
│  │  websocket_mgr.py   │  │     config.py       │  │    logging.py       ││
│  │                     │  │                     │  │                     ││
│  │ • connect()         │  │ • get_config()      │  │ • get_logger()      ││
│  │ • disconnect()      │  │ • validate_env()    │  │ • PerformanceTimer  ││
│  │ • broadcast()       │  │ • Settings class    │  │ • log_job_event()   ││
│  └─────────────────────┘  └─────────────────────┘  └─────────────────────┘│
│                                                                             │
├─────────────────────────────────────────────────────────────────────────────┤
│                          Models Layer (/models/)                             │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌─────────────────────┐  ┌─────────────────────┐  ┌─────────────────────┐│
│  │      base.py        │  │ document_models.py  │  │translation_models.py││
│  │                     │  │                     │  │                     ││
│  │ • ServiceType       │  │ • DocProcessRequest │  │ • TranslateRequest  ││
│  │ • JobStatus         │  │ • DocumentResults   │  │ • LanguageInfo      ││
│  │ • ProcessingJob     │  │ • TableData         │  │ • TranslationResult ││
│  │ • ErrorResponse     │  │ • PageData          │  │                     ││
│  └─────────────────────┘  └─────────────────────┘  └─────────────────────┘│
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Services Directory Structure

The services have been reorganized into a modular structure for better maintainability:

```
services/
├── document_intelligence/          # Document processing service (✅ WORKING)
│   ├── __init__.py
│   ├── service.py                 # Main service class
│   ├── processor.py               # Document processing logic
│   ├── table_extractor.py         # Table extraction logic
│   └── confidence_dashboard.py    # Confidence visualization
├── translation/                   # Translation service (✅ WORKING)
│   ├── __init__.py
│   └── service.py                 # Translation service implementation
├── transcription/                 # Transcription service (✅ WORKING)
│   ├── __init__.py
│   ├── service.py                 # Main service orchestrator
│   ├── fast_transcription_service.py  # Azure REST API client
│   ├── transcript_processor.py    # Result processing & chunking
│   └── output_generator.py        # File generation & packaging
├── storage/                       # Storage service (✅ Working)
│   ├── __init__.py
│   └── service.py                 # Azure Blob Storage operations
├── websocket/                     # WebSocket management
│   ├── __init__.py
│   └── manager.py                 # WebSocket connection management
└── shared/                        # Shared utilities
    ├── __init__.py
    └── field_accessor.py          # Universal field accessor helper
```

#### Service Import Pattern
```python
# Import services using the new structure:
from services.document_intelligence import get_document_intelligence_service
from services.translation import get_translation_service
from services.transcription import get_transcription_service
from services.storage import get_storage_service
from services.websocket import get_websocket_manager

# Import shared utilities:
from services.shared.field_accessor import get_field, get_nested_field
```

### Core Components

1. **FastAPI Application** (`main.py`)
   - CORS middleware for frontend communication
   - WebSocket support for real-time updates
   - Structured error handling
   - Request/response validation

2. **Service Layer** (`/services/`)
   - **Document Intelligence Service** (✅ Fully operational)
     - Wraps Azure Document Intelligence SDK
     - Comprehensive document analysis with table extraction
     - Confidence scoring and visualization
     - Results packaging in structured ZIP format
     - Modularized into processor, table_extractor, and dashboard components
   - **Transcription Service** (✅ Fully operational)
     - Uses Azure Speech Services fast transcription REST API
     - Speaker diarization with statistical analysis
     - Smart 1-minute chunking preserving sentences
     - Multiple output formats (TXT, SRT, VTT, JSON)
     - Comprehensive speaker analysis reports
   - **Translation Service** (✅ Backend operational, 🚧 Frontend needs fixing - 2025-12-22)
     - Backend fully working with Azure Translator REST API
     - Text extraction from DOCX files implemented
     - 137 language support confirmed
     - Backend tests passing (test_translation_docx.py)
     - **Issue**: Frontend still sending invalid source language parameter
     - Document translation with ZIP packaging working in backend
     - Real-time progress updates via WebSocket ready
     - Job management integration complete
   - **Storage Service** (✅ Working with local/Azure storage)
   - **WebSocket Manager** (✅ Working for real-time updates)

3. **API Layer** (`/api/`)
   - RESTful endpoints for each service
   - WebSocket endpoints for real-time updates
   - Request validation and response formatting
   - Error handling and status codes

4. **Models** (`/models/`)
   - Pydantic models for request/response validation
   - Azure response models
   - Job and status models

5. **Utilities** (`/utils/`)
   - **Azure Clients**: Manages SDK instances and connections
   - **File Handler**: Temp file management, ZIP creation, blob storage
   - **Job Manager**: Job queue, status tracking, progress updates
   - **WebSocket Manager**: Connection handling, broadcasting
   - **Config**: Environment variables and settings
   - **Logging**: Structured logging with performance tracking

## Quick Start

```bash
cd backend
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -r requirements.txt
uvicorn main:app --reload
```

## API Endpoints

### Document Intelligence
```
POST   /api/document-intelligence/process
POST   /api/document-intelligence/estimate-cost
GET    /api/document-intelligence/status/{job_id}
GET    /api/document-intelligence/results/{job_id}
```

### Translation
```
POST   /api/translation/translate-text
POST   /api/translation/translate-document
POST   /api/translation/estimate-cost
GET    /api/translation/languages
GET    /api/translation/status/{job_id}
GET    /api/translation/results/{job_id}
POST   /api/translation/detect-language
POST   /api/translation/translate-batch
```

### Transcription
```
POST   /api/transcription/transcribe
POST   /api/transcription/estimate-cost
GET    /api/transcription/status/{job_id}
GET    /api/transcription/results/{job_id}
```

### WebSocket
```
WS     /ws/{job_id}
```

## Development Workflow

### Adding a New Service
1. Create service class in `/services/`
2. Define request/response models in `/models/`
3. Create API endpoints in `/api/`
4. Add tests in `/tests/`
5. Update documentation

### Testing
```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=.

# Run specific test file
pytest tests/test_document_intelligence.py
```

## Environment Variables
See `.env.example` for required variables:
- Azure service endpoints and keys
- Storage configuration
- Application settings

## Error Handling
All errors follow a consistent format:
```json
{
  "error": {
    "code": "ERROR_CODE",
    "message": "Human-readable message",
    "details": {}
  }
}
```

## WebSocket Protocol
Real-time updates follow this format:
```json
{
  "type": "status_update",
  "job_id": "uuid",
  "status": "processing",
  "progress": 45,
  "message": "Processing page 3 of 7"
}
```

## Recent Learnings & Implementation Details

### Transcription Service Implementation (NEW - 2025-06-16)
1. **Azure Fast Transcription API**: Uses REST endpoint instead of SDK:
   - Endpoint: `https://{region}.stt.speech.microsoft.com/speechtotext/transcriptions:transcribe`
   - Multipart form data with audio file and configuration
   - Supports files up to 300MB and 2 hours duration
   - Returns comprehensive JSON with speaker diarization

2. **Smart Transcript Chunking**: 1-minute chunks with sentence preservation:
   ```python
   # Chunks maintain complete sentences
   # Format: [mm:ss-mm:ss][Speaker X] Complete sentences...
   # Multiple speakers in a chunk are properly labeled
   ```

3. **Result Package Structure**: Comprehensive ZIP with multiple formats:
   ```
   {job_id}_transcription_results.zip
   ├── {filename}_transcript.txt          # Formatted with timestamps
   ├── {filename}_transcript_detailed.json # Full Azure response
   ├── {filename}_transcript_summary.txt   # Statistics & metadata
   ├── {filename}_transcript.srt          # Subtitle format
   ├── {filename}_transcript.vtt          # WebVTT format
   └── {filename}_speaker_analysis.txt    # Detailed speaker stats
   ```

4. **Speaker Analysis Features**:
   - Speaker identification and statistics
   - Speaking time percentage for each speaker
   - Word count and phrase count per speaker
   - Speaker transition analysis
   - Conversation dynamics metrics

### Document Intelligence Service Implementation
1. **Azure SDK Changes**: The new Azure Document Intelligence SDK requires:
   - Using `AnalyzeDocumentRequest` with `bytes_source` for document content
   - Model names must be prefixed with "prebuilt-" (e.g., "prebuilt-layout")
   - Results come as objects with potential string representations for tables

2. **Table Processing Fix**: Tables in Azure responses may come as string representations:
   ```python
   # Critical fix for table parsing
   if isinstance(table, str):
       table = ast.literal_eval(table)
   ```

3. **Result Structure**: The service creates a comprehensive ZIP package:
   ```
   results.zip
   ├── analysis_summary.json      # Overall statistics
   ├── confidence_dashboard.png   # Visual quality metrics
   ├── document_tables.xlsx       # All tables in Excel format
   ├── document.md               # Full document in markdown
   ├── azure_response.json       # Raw Azure API response
   ├── csv/                      # Individual table CSV files
   │   ├── doc_pdf_page1_table0.csv
   │   └── doc_pdf_page2_table1.csv
   └── md/md_pages/             # Individual page markdown files
       ├── doc_pdf_page1.md
       └── doc_pdf_page2.md
   ```

4. **Progress Tracking**: Real-time updates via WebSocket:
   - 10%: Starting document analysis
   - 20%: Sending to Azure
   - 30-65%: Polling Azure for completion
   - 70%: Processing results
   - 80-90%: Creating visualizations and packaging
   - 100%: Complete

### Job Management Pattern
```python
# Job lifecycle
create_job() → queue_job() → process_job() → update_status() → complete_job()
                                    │
                                    └── broadcast_progress() → WebSocket
```

### Error Handling Hierarchy
```
AzureServiceException
├── DocumentProcessingException
├── TranslationException
└── TranscriptionException

FileException
├── FileValidationError
├── FileStorageError
└── FileNotFoundError
```

### Performance Optimizations
1. **Connection Pooling**: Azure clients are singleton instances
2. **Async Processing**: All I/O operations are async
3. **Memory Management**: Stream large files instead of loading to memory
4. **Progress Throttling**: Limit WebSocket updates to prevent flooding

### Security Implementation
1. **File Validation**: 
   - Check MIME types match extensions
   - Enforce size limits (50MB default)
   - Scan for malicious content patterns

2. **API Security**:
   - CORS restricted to frontend origin
   - Rate limiting per IP
   - Request size limits
   - Input sanitization

3. **Storage Security**:
   - Temporary files deleted after processing
   - Blob storage with SAS tokens
   - No direct file system access from API

## Backend Service Implementation Guide

### Document Intelligence Service Architecture (Fully Implemented Reference)

The Document Intelligence service serves as the reference implementation for all backend services. Here's how it's structured and integrated:

#### 1. **API Layer Structure** (`/backend/api/document_intelligence.py`)
- **Standard Endpoints Pattern**:
  ```
  POST /api/{service}/process         - Main processing with file upload
  POST /api/{service}/estimate-cost   - Pre-processing cost estimation
  GET  /api/{service}/status/{job_id} - Real-time job status
  GET  /api/{service}/results/{job_id} - Download processed results
  GET  /api/{service}/results/{job_id}/metadata - Get result metadata
  POST /api/{service}/cancel/{job_id} - Cancel running job
  GET  /api/{service}/supported-formats - List supported file formats
  POST /api/{service}/batch           - Batch processing multiple files
  GET  /api/{service}/health          - Service health check
  ```

#### 2. **Service Layer Pattern** (`/backend/services/{service_name}/`)
Each service follows this modular structure:
- `service.py` - Main service class with Azure SDK integration
- `processor.py` - Core processing logic and orchestration
- `{feature}_extractor.py` - Specialized processing modules
- `{output}_generator.py` - Result formatting and packaging

#### 3. **Job Processing Flow**
```
1. Frontend Request → API Endpoint
2. Create Job (job_manager) → Return job_id immediately
3. Upload File → Azure Blob Storage
4. Background Task → Process asynchronously
5. Progress Updates → WebSocket broadcasts
6. Results Package → ZIP and upload to blob
7. Completion Notice → WebSocket with download URL
```

#### 4. **Key Implementation Patterns**

##### API Endpoint Pattern
```python
@router.post("/process")
async def process_document(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    analysis_type: str = Form(default="layout"),
    extract_tables: bool = Form(default=True),
    # ... other parameters
):
    # 1. Validate file and parameters
    # 2. Create job with job_manager
    # 3. Upload file to blob storage
    # 4. Queue background processing task
    # 5. Return job info immediately (non-blocking)
```

##### Background Processing Pattern
```python
async def _process_document_task(job_id: str, blob_path: str, options: dict):
    try:
        # Update job status to PROCESSING
        await job_manager.update_job_status(job_id, JobStatus.PROCESSING)
        
        # Download file locally for processing
        local_path = await download_from_blob(blob_path)
        
        # Process with progress callbacks
        results = await service.process_document(
            local_path, 
            job_id,
            progress_callback=lambda p: websocket_manager.broadcast_job_update(
                job_id, {"progress": p, "status": "processing"}
            )
        )
        
        # Package results
        results_path = await create_results_package(job_id, results)
        
        # Update job as completed
        await job_manager.complete_job(job_id, results_path, metadata)
        
        # Broadcast completion
        await websocket_manager.broadcast_job_completion(job_id, download_url)
        
    except Exception as e:
        # Update job as failed
        await job_manager.fail_job(job_id, str(e))
        # Broadcast error
        await websocket_manager.broadcast_job_error(job_id, str(e))
    finally:
        # Cleanup temp files
        cleanup_temp_files(local_path)
```

##### Service Method Pattern
```python
class DocumentIntelligenceService:
    async def process_document(
        self,
        file_path: str,
        job_id: str,
        options: ProcessingOptions,
        progress_callback: Optional[Callable] = None
    ) -> ProcessingResults:
        # 1. Initialize Azure client
        client = self._get_or_create_client()
        
        # 2. Start Azure operation
        poller = await client.begin_analyze_document(
            model_id=options.model,
            document=file_path
        )
        
        # 3. Poll with progress updates
        while not poller.done():
            if progress_callback:
                progress_callback({
                    "percentage": calculate_progress(),
                    "message": "Analyzing document...",
                    "current_step": "extraction"
                })
            await asyncio.sleep(1)
        
        # 4. Process results
        result = await poller.result()
        
        # 5. Extract and format data
        extracted_data = self._extract_data(result)
        
        # 6. Generate outputs (tables, text, etc.)
        outputs = await self._generate_outputs(extracted_data, options)
        
        return ProcessingResults(
            outputs=outputs,
            metadata=self._generate_metadata(result)
        )
```

##### WebSocket Integration Pattern
```python
# In processing functions:
await websocket_manager.broadcast_job_update(
    job_id,
    {
        "type": "job_update",
        "job_id": job_id,
        "status": "processing",
        "progress": {
            "progress_percentage": 50,
            "current_step": "Extracting tables",
            "message": "Found 3 tables, processing..."
        }
    }
)

# On completion:
await websocket_manager.broadcast_job_update(
    job_id,
    {
        "type": "job_completed",
        "job_id": job_id,
        "status": "completed",
        "data": {
            "download_url": results_url,
            "character_count": 15420,
            "processing_time": 12.5
        }
    }
)
```

##### Results Packaging Pattern
```python
async def create_results_package(job_id: str, results: ProcessingResults) -> str:
    # Create organized directory structure
    output_dir = f"/tmp/{job_id}"
    os.makedirs(f"{output_dir}/text", exist_ok=True)
    os.makedirs(f"{output_dir}/tables", exist_ok=True)
    os.makedirs(f"{output_dir}/metadata", exist_ok=True)
    
    # Save all outputs
    for output in results.outputs:
        save_path = f"{output_dir}/{output.type}/{output.filename}"
        await save_file(save_path, output.content)
    
    # Create summary JSON
    summary = {
        "job_id": job_id,
        "processed_at": datetime.utcnow().isoformat(),
        "statistics": results.metadata,
        "files": [{"path": f.path, "type": f.type} for f in results.outputs]
    }
    
    # Create ZIP (with UUID prefix removal)
    zip_path = f"/tmp/{job_id}_results.zip"
    create_zip(output_dir, zip_path)
    
    # Upload to blob storage
    blob_path = f"results/{job_id}/results.zip"
    await upload_to_blob(zip_path, blob_path)
    
    return blob_path
```

#### 5. **Frontend-Backend Integration Points**

##### Request Flow
```javascript
// Frontend (DocumentIntelligence.vue)
const result = await documentIntelligenceService.processDocument(
    selectedFile.value,
    processingOptions,
    uploadProgressCallback
)
// Returns immediately with job_id

// Subscribe to WebSocket for updates
websocketService.subscribe(jobId, '*', handleWebSocketUpdate)
```

##### WebSocket Update Handling
```javascript
// Frontend handles real-time updates
const handleWebSocketUpdate = (data) => {
    if (data.type === 'job_update') {
        progress.value = data.progress.progress_percentage
        currentStage.value = data.progress.current_step
        stageDetails.value = data.progress.message
    } else if (data.type === 'job_completed') {
        processingStatus.value = 'completed'
        characterCount.value = data.data.character_count
        // Enable download button
    }
}
```

#### 6. **Implementation Checklist for New Services**

When implementing Translation or Transcription services, ensure:

- [ ] API endpoints follow the standard pattern (all 9 endpoints)
- [ ] Service class implements proper Azure SDK integration
- [ ] Background task pattern for async processing
- [ ] WebSocket updates at each processing stage
- [ ] Proper job management integration
- [ ] Results packaging in organized ZIP files
- [ ] Error handling with user-friendly messages
- [ ] Cost estimation based on actual Azure pricing
- [ ] File validation and size limits
- [ ] Cleanup of temporary files
- [ ] Comprehensive logging with correlation IDs
- [ ] Health check endpoint with service status
- [ ] Batch processing support
- [ ] Metadata generation for results
- [ ] Progress tracking with meaningful messages

#### 7. **Common Pitfalls to Avoid**

1. **Don't block on processing** - Always use background tasks
2. **Don't forget cleanup** - Always remove temp files
3. **Don't skip validation** - Check file types and sizes
4. **Don't ignore errors** - Properly update job status on failure
5. **Don't forget progress** - Send regular WebSocket updates
6. **Don't hardcode paths** - Use configuration and blob storage
7. **Don't skip metadata** - Include processing stats for UI

### Service Base Class Pattern

For consistency across services, use this base pattern:

```python
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, Callable

class BaseAzureService(ABC):
    """Base class for all Azure Cognitive Services."""
    
    def __init__(self):
        self.config = get_config()
        self.client = None
        self._initialize_client()
    
    @abstractmethod
    def _initialize_client(self):
        """Initialize the Azure service client."""
        pass
    
    @abstractmethod
    async def process(
        self,
        input_data: Any,
        job_id: str,
        options: Dict[str, Any],
        progress_callback: Optional[Callable] = None
    ) -> Dict[str, Any]:
        """Process the input data."""
        pass
    
    @abstractmethod
    async def estimate_cost(
        self,
        input_metadata: Dict[str, Any]
    ) -> Dict[str, float]:
        """Estimate processing cost."""
        pass
    
    @abstractmethod
    async def validate_input(
        self,
        input_data: Any
    ) -> bool:
        """Validate input before processing."""
        pass
    
    def _handle_azure_error(self, error: Exception) -> Exception:
        """Convert Azure errors to our custom exceptions."""
        if isinstance(error, ResourceNotFoundError):
            return FileNotFoundException(str(error))
        elif isinstance(error, ServiceRequestError):
            return AzureServiceException(str(error))
        return error
```

### Testing Patterns

#### Mock Azure Services
```python
@pytest.fixture
def mock_document_intelligence_client():
    """Mock Azure Document Intelligence client."""
    with patch('services.document_intelligence.service.DocumentIntelligenceClient') as mock:
        mock_instance = Mock()
        mock.return_value = mock_instance
        
        # Mock analyze_document method
        mock_poller = Mock()
        mock_poller.done.side_effect = [False, False, True]
        mock_poller.result.return_value = {
            'pages': [{'pageNumber': 1}],
            'tables': [{'rowCount': 3, 'columnCount': 2}],
            'content': 'Sample document content'
        }
        
        mock_instance.begin_analyze_document.return_value = mock_poller
        yield mock_instance
```

#### Integration Test Pattern
```python
@pytest.mark.asyncio
async def test_document_processing_flow():
    """Test complete document processing flow."""
    # 1. Upload file
    with open('test_doc.pdf', 'rb') as f:
        response = await client.post(
            '/api/document-intelligence/process',
            files={'file': f}
        )
    
    assert response.status_code == 200
    job_id = response.json()['job_id']
    
    # 2. Check status
    status_response = await client.get(
        f'/api/document-intelligence/status/{job_id}'
    )
    assert status_response.json()['status'] in ['pending', 'processing']
    
    # 3. Wait for completion (mock)
    await asyncio.sleep(2)
    
    # 4. Download results
    results_response = await client.get(
        f'/api/document-intelligence/results/{job_id}'
    )
    assert results_response.status_code == 200
    assert results_response.headers['content-type'] == 'application/zip'
```

### Performance Optimization Tips

1. **Connection Pooling**: Reuse Azure client instances
2. **Async Operations**: Use asyncio for all I/O operations
3. **Streaming**: Stream large files instead of loading to memory
4. **Caching**: Cache frequently accessed data (language lists, etc.)
5. **Batch Processing**: Process multiple items in single Azure calls
6. **Progress Throttling**: Limit WebSocket updates to prevent flooding

### Monitoring and Logging

```python
# Structured logging pattern
logger.info(
    "Document processed",
    extra={
        "job_id": job_id,
        "document_name": document_name,
        "pages": page_count,
        "tables_extracted": table_count,
        "processing_time": processing_time,
        "service": "document_intelligence"
    }
)

# Performance tracking
with PerformanceTimer(logger, "azure_api_call"):
    result = await client.analyze_document(...)
```

## Backend Service Implementation Guide

### Standard API Endpoint Pattern
Every service should implement these standard endpoints:

```python
# Standard endpoint structure for all services
@router.post("/{service}/process")         # Main processing endpoint
@router.post("/{service}/estimate-cost")   # Cost estimation
@router.get("/{service}/status/{job_id}")  # Job status
@router.get("/{service}/results/{job_id}") # Download results
@router.get("/{service}/results/{job_id}/metadata") # Result metadata
@router.post("/{service}/cancel/{job_id}") # Cancel job
@router.get("/{service}/supported-formats") # List formats
@router.post("/{service}/batch")           # Batch processing
@router.get("/{service}/health")           # Service health
```

### Background Task Pattern
All processing should be non-blocking:

```python
@router.post("/process")
async def process_document(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    options: ProcessingOptions = Depends()
):
    # 1. Validate input
    validate_file(file)
    
    # 2. Create job
    job_id = await job_manager.create_job(
        service_type=ServiceType.DOCUMENT_INTELLIGENCE,
        input_file=file.filename
    )
    
    # 3. Upload file to storage
    blob_path = await storage_service.upload_file(
        file=await file.read(),
        path=f"jobs/{job_id}/input/{file.filename}"
    )
    
    # 4. Queue background task
    background_tasks.add_task(
        _process_document_task,
        job_id=job_id,
        blob_path=blob_path,
        options=options.dict()
    )
    
    # 5. Return immediately
    return {"job_id": job_id, "status": "queued"}
```

### WebSocket Integration Pattern
Every service must send progress updates:

```python
async def _process_task(job_id: str, **kwargs):
    try:
        # Update status
        await job_manager.update_job_status(job_id, JobStatus.PROCESSING)
        
        # Send WebSocket update
        await websocket_manager.broadcast_job_update(
            job_id,
            {
                "type": "job_started",
                "job_id": job_id,
                "status": "processing",
                "message": "Starting document analysis..."
            }
        )
        
        # Process with progress callbacks
        def progress_callback(progress: int, message: str):
            asyncio.create_task(
                websocket_manager.broadcast_job_update(
                    job_id,
                    {
                        "type": "job_update",
                        "job_id": job_id,
                        "progress": progress,
                        "message": message
                    }
                )
            )
        
        # ... processing logic with callbacks ...
        
    except Exception as e:
        await job_manager.fail_job(job_id, str(e))
        await websocket_manager.broadcast_job_update(
            job_id,
            {
                "type": "job_failed",
                "job_id": job_id,
                "error": str(e)
            }
        )
```

### Result Packaging Pattern
All services should package results consistently:

```python
async def create_results_package(job_id: str, results: Any) -> str:
    """Create standardized results package."""
    output_dir = f"/tmp/{job_id}_output"
    os.makedirs(output_dir, exist_ok=True)
    
    # 1. Create summary
    summary = {
        "job_id": job_id,
        "service": "document_intelligence",
        "processed_at": datetime.utcnow().isoformat(),
        "statistics": {
            # Service-specific stats
        },
        "files": []
    }
    
    # 2. Save all outputs with consistent naming
    # Use original filename as base
    base_name = Path(original_filename).stem
    
    # 3. Create organized directory structure
    os.makedirs(f"{output_dir}/raw", exist_ok=True)
    os.makedirs(f"{output_dir}/processed", exist_ok=True)
    os.makedirs(f"{output_dir}/metadata", exist_ok=True)
    
    # 4. Save files and update summary
    # ... save logic ...
    
    # 5. Create ZIP
    zip_path = f"/tmp/{job_id}_results.zip"
    shutil.make_archive(zip_path.replace('.zip', ''), 'zip', output_dir)
    
    # 6. Upload to blob storage
    blob_path = f"results/{job_id}/results.zip"
    download_url = await storage_service.upload_file(
        file_path=zip_path,
        blob_path=blob_path
    )
    
    # 7. Cleanup temp files
    shutil.rmtree(output_dir)
    os.remove(zip_path)
    
    return download_url
```

### Service Class Pattern
All services should follow this structure:

```python
class BaseAzureService:
    """Base class for all Azure services."""
    
    def __init__(self):
        self.client = None
        self._initialize_client()
    
    def _initialize_client(self):
        """Initialize Azure client with retry logic."""
        raise NotImplementedError
    
    async def health_check(self) -> bool:
        """Check if service is healthy."""
        try:
            # Service-specific health check
            return True
        except Exception:
            return False
    
    async def process(self, *args, **kwargs):
        """Main processing method."""
        raise NotImplementedError

class DocumentIntelligenceService(BaseAzureService):
    """Document Intelligence service implementation."""
    
    def _initialize_client(self):
        self.client = DocumentIntelligenceClient(
            endpoint=config.AZURE_DOC_INTELLIGENCE_ENDPOINT,
            credential=AzureKeyCredential(config.AZURE_DOC_INTELLIGENCE_KEY)
        )
    
    async def process(self, file_path: str, options: dict) -> dict:
        # Implementation
        pass
```

### Testing Pattern
Every service needs comprehensive tests:

```python
# tests/test_[service_name].py
import pytest
from unittest.mock import Mock, patch

class TestDocumentIntelligenceService:
    @pytest.fixture
    def service(self):
        with patch('services.document_intelligence.service.DocumentIntelligenceClient'):
            return DocumentIntelligenceService()
    
    @pytest.fixture
    def sample_file(self, tmp_path):
        file_path = tmp_path / "test.pdf"
        file_path.write_bytes(b"PDF content")
        return str(file_path)
    
    async def test_process_document_success(self, service, sample_file):
        # Arrange
        mock_result = Mock()
        service.client.begin_analyze_document.return_value = mock_result
        
        # Act
        result = await service.process(sample_file, {})
        
        # Assert
        assert result is not None
        service.client.begin_analyze_document.assert_called_once()
    
    async def test_process_document_error_handling(self, service, sample_file):
        # Test error scenarios
        pass
```

## Implementation Checklist for New Services

When implementing Translation or Transcription services:

- [ ] Create service directory structure under `/services/`
- [ ] Implement all 9 standard API endpoints
- [ ] Create service class inheriting from BaseAzureService
- [ ] Implement background task processing
- [ ] Add WebSocket progress updates at each stage
- [ ] Create result packaging following standard pattern
- [ ] Define Pydantic models for requests/responses
- [ ] Add comprehensive error handling
- [ ] Implement health check endpoint
- [ ] Write unit and integration tests
- [ ] Add service to main.py router registration
- [ ] Update API documentation
- [ ] Add service-specific configuration
- [ ] Create Azure service mocks for testing
- [ ] Document any service-specific patterns

## Common Pitfalls and Solutions

1. **Blocking Operations**: Always use background tasks for processing
2. **Memory Issues**: Stream large files, don't load into memory
3. **Missing Progress Updates**: Send updates at least every 5 seconds
4. **Poor Error Messages**: Provide actionable error information
5. **Cleanup Failures**: Always cleanup in try/finally blocks
6. **Hardcoded Values**: Use configuration for all settings
7. **Missing Validation**: Validate all inputs before processing
8. **No Retry Logic**: Implement exponential backoff for Azure calls
9. **Poor Logging**: Use structured logging with correlation IDs
10. **No Health Checks**: Implement proper health monitoring

## Backend Refactoring Plan (2025-06-22)

### Current State Analysis

#### Code Duplication Metrics
- **~40% duplicate code** across the three services (Document Intelligence, Translation, Transcription)
- **3 separate implementations** of the same patterns:
  - File upload/download logic repeated in each API file
  - Background task processing duplicated 3 times
  - WebSocket update patterns copied across services
  - ZIP packaging implemented separately for each service
  - Error handling inconsistent between services

#### Identified Issues

1. **API Layer Duplication** (`/api/`):
   - Each service has nearly identical endpoint patterns
   - Background task processing logic is copy-pasted
   - File handling code is duplicated
   - Progress callback patterns are inconsistent

2. **Service Layer Inconsistencies** (`/services/`):
   - Document Intelligence: Well-structured with separate modules
   - Translation: Monolithic service.py file (307 lines)
   - Transcription: Good structure but doesn't follow common patterns
   - No shared base classes or utilities

3. **Unused Code**:
   - `services/shared/field_accessor.py` - Not used anywhere
   - Duplicate methods in job_manager (complete_job, fail_job)
   - Unused imports in azure_clients.py

4. **Technical Debt**:
   - No standardized error handling across services
   - Inconsistent progress reporting
   - Different approaches to file processing
   - No shared testing utilities

### Target Architecture

#### New Base Class Hierarchy

```
services/
├── base/                          # NEW: Base classes for all services
│   ├── __init__.py
│   ├── base_service.py           # Abstract base for Azure services
│   ├── base_processor.py         # Common processing patterns
│   └── base_api.py              # Base class for API routers
├── document_intelligence/         # Refactored to use base classes
├── translation/                   # Refactored to modular structure
├── transcription/                 # Refactored to use base classes
└── shared/                        # Refactored shared utilities
    ├── file_processor.py         # Unified file operations
    ├── job_processor.py          # Common job processing
    └── result_packager.py        # Standardized ZIP creation
```

#### Base Service Architecture

```python
# services/base/base_service.py
class BaseAzureService(ABC):
    """Base class for all Azure Cognitive Services."""
    
    def __init__(self):
        self.config = get_config()
        self.client = None
        self.file_processor = FileProcessor()
        self.result_packager = ResultPackager()
        self._initialize_client()
    
    @abstractmethod
    async def process(
        self,
        file_path: str,
        job_id: str,
        options: Dict[str, Any],
        progress_callback: Optional[ProgressCallback] = None
    ) -> ProcessingResult:
        """Main processing method all services must implement."""
        pass
    
    async def create_results_package(
        self,
        job_id: str,
        results: ProcessingResult,
        original_filename: str
    ) -> str:
        """Standardized result packaging."""
        return await self.result_packager.create_package(
            job_id, results, original_filename, self.service_type
        )
```

#### Shared Utilities Design

1. **FileProcessor** (`services/shared/file_processor.py`):
   - Upload to blob storage
   - Download from blob storage
   - Temporary file management
   - File validation and sanitization

2. **JobProcessor** (`services/shared/job_processor.py`):
   - Background task execution wrapper
   - Progress tracking standardization
   - Error handling and retry logic
   - WebSocket update integration

3. **ResultPackager** (`services/shared/result_packager.py`):
   - Consistent ZIP structure creation
   - Metadata generation
   - File organization patterns
   - Upload to blob storage

### Refactoring Roadmap

#### Phase 1: Create Base Infrastructure (Week 1)
- [ ] Create `services/base/` directory structure
- [ ] Implement BaseAzureService abstract class
- [ ] Implement BaseProcessor for common processing patterns
- [ ] Create BaseAPIRouter for standardized endpoints
- [ ] Move shared utilities from utils/ to services/shared/
- [ ] Create comprehensive tests for base classes

#### Phase 2: Refactor Document Intelligence (Week 2)
- [ ] Update DocumentIntelligenceService to inherit from BaseAzureService
- [ ] Extract common patterns to base classes
- [ ] Use shared FileProcessor for file operations
- [ ] Implement standardized progress callbacks
- [ ] Update API endpoints to use BaseAPIRouter
- [ ] Ensure all tests pass

#### Phase 3: Refactor Translation Service (Week 3)
- [ ] Split monolithic service.py into modules:
  - [ ] text_translator.py
  - [ ] document_translator.py
  - [ ] language_detector.py
- [ ] Inherit from BaseAzureService
- [ ] Remove duplicate file handling code
- [ ] Standardize progress reporting
- [ ] Update API to use BaseAPIRouter
- [ ] Add missing endpoint implementations
- [ ] Update and expand tests

#### Phase 4: Refactor Transcription Service (Week 4)
- [ ] Update to use BaseAzureService
- [ ] Consolidate output generation with ResultPackager
- [ ] Standardize progress callbacks
- [ ] Update API to use BaseAPIRouter
- [ ] Remove duplicate code
- [ ] Ensure test coverage

#### Phase 5: Cleanup and Optimization (Week 5)
- [ ] Remove unused code (field_accessor.py, etc.)
- [ ] Consolidate duplicate job_manager methods
- [ ] Update all imports throughout codebase
- [ ] Performance testing and optimization
- [ ] Documentation updates
- [ ] Final integration testing

### Implementation Progress Tracking

#### Phase 1 Progress: Base Infrastructure
- [x] BaseAzureService class created ✅ (2025-06-22)
- [ ] BaseProcessor class created
- [ ] BaseAPIRouter class created
- [x] FileProcessor utility created ✅ (2025-06-22)
- [ ] JobProcessor utility created
- [ ] ResultPackager utility created
- [x] Unit tests for BaseAzureService ✅ (2025-06-22)
- [x] Unit tests for FileProcessor ✅ (2025-06-22)
- [ ] Integration tests for shared utilities

#### Phase 2 Progress: Document Intelligence
- [ ] Service refactored to use base classes
- [ ] API endpoints migrated to BaseAPIRouter
- [ ] File operations using FileProcessor
- [ ] Results using ResultPackager
- [ ] All existing tests passing
- [ ] New tests for refactored code

#### Phase 3 Progress: Translation Service
- [ ] Service split into modules
- [ ] Modules using base classes
- [ ] API endpoints standardized
- [ ] Duplicate code removed
- [ ] All tests updated and passing
- [ ] New tests for modular structure

#### Phase 4 Progress: Transcription Service
- [ ] Service using base classes
- [ ] Output generation standardized
- [ ] API endpoints consistent
- [ ] Duplicate code eliminated
- [ ] Tests updated and passing

#### Phase 5 Progress: Cleanup
- [ ] Unused files removed
- [ ] Job manager consolidated
- [ ] All imports updated
- [ ] Performance benchmarks complete
- [ ] Documentation fully updated
- [ ] Integration tests passing

### Code Comparison Examples

#### Before Refactoring (Translation API):
```python
# Duplicate code in translation.py
async def _process_translation_task(job_id, temp_path, ...):
    try:
        await job_manager.update_job_status(job_id, JobStatus.PROCESSING)
        # ... 100+ lines of processing logic
        await websocket_manager.broadcast_job_update(...)
        # ... more duplicate code
```

#### After Refactoring:
```python
# Using base classes and shared utilities
class TranslationAPIRouter(BaseAPIRouter):
    service_type = ServiceType.TRANSLATION
    
    async def process_file(self, file_path: str, options: Dict) -> ProcessingResult:
        return await self.service.translate_document(
            file_path, options['target_language'], options.get('source_language')
        )
```

### Benefits Analysis

1. **Code Reduction**: ~40% less code through consolidation
2. **Consistency**: All services follow identical patterns
3. **Maintainability**: Common logic in one place
4. **Testability**: Base classes tested once, inherited everywhere
5. **Extensibility**: New services can be added in hours, not days
6. **Performance**: Optimizations benefit all services

### Maintenance Guidelines

#### Updating This Plan
1. **Daily Updates**: Check off completed items at end of each day
2. **Weekly Reviews**: Update timeline and adjust phases as needed
3. **Blocker Documentation**: Add notes about any blocking issues
4. **Decision Log**: Document any architectural decisions made

#### Code Review Checklist
- [ ] Uses appropriate base classes
- [ ] No duplicate code introduced
- [ ] Follows established patterns
- [ ] Includes comprehensive tests
- [ ] Updates documentation
- [ ] Maintains backwards compatibility

#### Testing Requirements
1. **Unit Tests**: All new base classes and utilities
2. **Integration Tests**: Service interactions with base classes
3. **API Tests**: Ensure endpoints work as before
4. **Performance Tests**: No regression in processing times
5. **End-to-End Tests**: Full workflow validation

#### Documentation Standards
1. **Code Comments**: Explain why, not what
2. **Docstrings**: All public methods and classes
3. **README Updates**: Keep user docs current
4. **CLAUDE.md Updates**: Track architectural changes
5. **API Documentation**: OpenAPI/Swagger updates

### Risk Mitigation

1. **Backwards Compatibility**: All API endpoints must maintain same interface
2. **Testing Coverage**: No code merged without tests
3. **Gradual Migration**: One service at a time
4. **Rollback Plan**: Git branches for each phase
5. **Performance Monitoring**: Benchmark before and after

### Success Metrics

1. **Code Duplication**: Reduce from 40% to <5%
2. **Test Coverage**: Maintain >80% coverage
3. **Performance**: No regression in processing times
4. **Development Time**: New features 50% faster to implement
5. **Bug Rate**: Reduce service-related bugs by 70%