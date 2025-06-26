# Azure Cognitive Services API Reference

Complete API documentation for all implemented services in the Cognitive Services Frontend project.

## Table of Contents
1. [Document Intelligence API](#document-intelligence-api)
2. [Translation API](#translation-api)
3. [Transcription API](#transcription-api)
4. [Storage API](#storage-api)
5. [WebSocket API](#websocket-api)
6. [Common Response Formats](#common-response-formats)
7. [Error Codes](#error-codes)

## Base Configuration

### Base URL
```
http://localhost:8000
```

### Authentication
⚠️ **Currently no authentication is implemented**. See [IMPLEMENTATION_GUIDE.md](./IMPLEMENTATION_GUIDE.md) for planned auth system.

### Request Headers
```http
Content-Type: application/json (for JSON requests)
Content-Type: multipart/form-data (for file uploads)
X-Correlation-ID: <optional-correlation-id>
```

## Document Intelligence API

### Process Document
Extract tables, text, and metadata from documents.

**Endpoint:** `POST /api/document-intelligence/process`

**Request:**
```http
POST /api/document-intelligence/process
Content-Type: multipart/form-data

file: <binary file data>
analysis_type: "layout" | "document" | "read" (default: "layout")
extract_tables: true | false (default: true)
extract_text: true | false (default: true)
output_format: "markdown" | "text" | "html" (default: "markdown")
include_confidence: true | false (default: true)
```

**Response:**
```json
{
  "success": true,
  "data": {
    "job_id": "123e4567-e89b-12d3-a456-426614174000",
    "status": "pending",
    "created_at": "2023-12-22T10:00:00Z"
  }
}
```

### Estimate Cost
Calculate processing cost before submission.

**Endpoint:** `POST /api/document-intelligence/estimate-cost`

**Request:**
```json
{
  "file_size_bytes": 1048576,
  "file_type": "application/pdf"
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "estimated_cost_usd": 0.15,
    "estimated_pages": 3,
    "confidence": "high"
  }
}
```

### Get Job Status
Check processing status of a document job.

**Endpoint:** `GET /api/document-intelligence/status/{job_id}`

**Response:**
```json
{
  "success": true,
  "data": {
    "job_id": "123e4567-e89b-12d3-a456-426614174000",
    "status": "processing",
    "progress": 65,
    "current_stage": "Extracting tables",
    "message": "Found 3 tables, processing..."
  }
}
```

### Download Results
Get processed document results as ZIP file.

**Endpoint:** `GET /api/document-intelligence/results/{job_id}`

**Response:** Binary ZIP file containing:
- `analysis_summary.json` - Processing statistics
- `confidence_dashboard.png` - Visual confidence metrics
- `document_tables.xlsx` - All tables in Excel format
- `document.md` - Full document in markdown
- `azure_response.json` - Raw Azure API response
- `csv/` - Individual table CSV files
- `md/` - Individual page markdown files

## Translation API

### Translate Text
Translate plain text between languages.

**Endpoint:** `POST /api/translation/translate-text`

**Request:**
```json
{
  "text": "Hello, world!",
  "target_language": "es",
  "source_language": "en"  // Optional, auto-detect if not provided
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "translated_text": "¡Hola, mundo!",
    "detected_language": "en",
    "confidence": 1.0
  }
}
```

### Translate Document
Translate entire documents while preserving formatting.

**Endpoint:** `POST /api/translation/translate-document`

**Request:**
```http
POST /api/translation/translate-document
Content-Type: multipart/form-data

file: <binary file data>
target_language: "es"
source_language: "auto"  // Optional
preserve_formatting: true
```

**Response:**
```json
{
  "success": true,
  "data": {
    "job_id": "456e7890-e89b-12d3-a456-426614174000",
    "status": "pending"
  }
}
```

### Get Supported Languages
List all supported languages for translation.

**Endpoint:** `GET /api/translation/languages`

**Response:**
```json
{
  "success": true,
  "data": {
    "languages": [
      {
        "code": "en",
        "name": "English",
        "native_name": "English",
        "direction": "ltr"
      },
      {
        "code": "es",
        "name": "Spanish",
        "native_name": "Español",
        "direction": "ltr"
      }
      // ... 135 more languages
    ],
    "total": 137
  }
}
```

## Transcription API

### Transcribe Audio
Convert audio to text with speaker diarization.

**Endpoint:** `POST /api/transcription/transcribe`

**Request:**
```http
POST /api/transcription/transcribe
Content-Type: multipart/form-data

file: <audio file data>
language: "en-US"  // Optional, auto-detect if not provided
enable_diarization: true
max_speakers: 10
output_format: "txt" | "srt" | "vtt" | "json"
```

**Response:**
```json
{
  "success": true,
  "data": {
    "job_id": "789e0123-e89b-12d3-a456-426614174000",
    "status": "pending",
    "estimated_duration_seconds": 180
  }
}
```

### Get Transcription Languages
List supported languages for transcription.

**Endpoint:** `GET /api/transcription/languages`

**Response:**
```json
{
  "success": true,
  "data": {
    "languages": [
      {
        "code": "en-US",
        "name": "English (United States)",
        "region": "United States"
      },
      {
        "code": "es-ES",
        "name": "Spanish (Spain)",
        "region": "Spain"
      }
      // ... 28 more languages
    ],
    "total": 30
  }
}
```

## Storage API

### Upload File
Upload file to blob storage.

**Endpoint:** `POST /api/storage/upload`

**Request:**
```http
POST /api/storage/upload
Content-Type: multipart/form-data

file: <binary file data>
path: "documents/reports/file.pdf"  // Optional path
```

**Response:**
```json
{
  "success": true,
  "data": {
    "blob_name": "documents/reports/file.pdf",
    "url": "https://storage.blob.core.windows.net/...",
    "size_bytes": 1048576
  }
}
```

### Download File
Download file from blob storage.

**Endpoint:** `GET /api/storage/download/{blob_name}`

**Response:** Binary file data

## WebSocket API

### Job-Specific Updates
Connect to receive updates for a specific job.

**Endpoint:** `WS /ws/{job_id}`

**Connection:**
```javascript
const ws = new WebSocket('ws://localhost:8000/ws/123e4567-e89b-12d3-a456-426614174000');
```

**Message Format:**
```json
{
  "type": "job_update",
  "job_id": "123e4567-e89b-12d3-a456-426614174000",
  "status": "processing",
  "progress": {
    "percentage": 45,
    "current_step": "Extracting tables",
    "message": "Found 3 tables, processing..."
  },
  "timestamp": "2023-12-22T10:01:30Z"
}
```

**Message Types:**
- `job_started` - Processing has begun
- `job_update` - Progress update
- `job_completed` - Processing finished successfully
- `job_failed` - Processing failed with error
- `connection_established` - WebSocket connected

## Common Response Formats

### Success Response
```json
{
  "success": true,
  "data": {
    // Service-specific data
  },
  "correlation_id": "550e8400-e29b-41d4-a716-446655440000"
}
```

### Error Response
```json
{
  "success": false,
  "error": {
    "code": "FILE_TOO_LARGE",
    "message": "File size exceeds 50MB limit",
    "details": {
      "max_size_mb": 50,
      "file_size_mb": 75.5
    }
  },
  "correlation_id": "550e8400-e29b-41d4-a716-446655440000"
}
```

### Job Status Values
- `pending` - Job created but not started
- `processing` - Job is being processed
- `completed` - Job finished successfully
- `failed` - Job failed with error
- `cancelled` - Job was cancelled

## Error Codes

### Client Errors (4xx)
- `400 BAD_REQUEST` - Invalid request parameters
- `401 UNAUTHORIZED` - Authentication required (future)
- `402 PAYMENT_REQUIRED` - Usage quota exceeded (future)
- `403 FORBIDDEN` - Access denied
- `404 NOT_FOUND` - Resource not found
- `413 FILE_TOO_LARGE` - File exceeds size limit
- `415 UNSUPPORTED_MEDIA_TYPE` - Invalid file type
- `422 UNPROCESSABLE_ENTITY` - Validation error
- `429 TOO_MANY_REQUESTS` - Rate limit exceeded

### Server Errors (5xx)
- `500 INTERNAL_SERVER_ERROR` - Unexpected error
- `502 BAD_GATEWAY` - Azure service error
- `503 SERVICE_UNAVAILABLE` - Service temporarily down
- `504 GATEWAY_TIMEOUT` - Processing timeout

### Custom Error Codes
- `AZURE_CONNECTION_ERROR` - Cannot connect to Azure
- `INVALID_FILE_FORMAT` - File format not supported
- `PROCESSING_FAILED` - Azure processing failed
- `QUOTA_EXCEEDED` - User quota exceeded
- `JOB_NOT_FOUND` - Job ID not found
- `RESULT_NOT_READY` - Results not yet available

## Rate Limits

⚠️ **Currently no rate limiting is implemented**

Planned limits:
- 100 requests per minute per IP
- 10 concurrent jobs per user
- 50MB max file size
- 1GB daily upload limit

## SDK Examples

### JavaScript/TypeScript
```javascript
import { CognitiveServicesClient } from './sdk/client';

const client = new CognitiveServicesClient({
  baseURL: 'http://localhost:8000',
  apiKey: 'your-api-key' // Future
});

// Process document
const job = await client.documentIntelligence.process({
  file: fileInput.files[0],
  extractTables: true,
  outputFormat: 'markdown'
});

// Wait for completion
const result = await client.jobs.waitForCompletion(job.job_id);
```

### Python
```python
from cognitive_services_sdk import Client

client = Client(
    base_url="http://localhost:8000",
    api_key="your-api-key"  # Future
)

# Translate text
result = client.translation.translate_text(
    text="Hello, world!",
    target_language="es"
)

print(result.translated_text)  # ¡Hola, mundo!
```

## Postman Collection

Import the Postman collection from `postman/cognitive-services-api.json` for easy testing of all endpoints.

## API Versioning

Currently using v1 (implicit). Future versions will use:
- URL versioning: `/api/v2/...`
- Header versioning: `X-API-Version: 2`

## Support

For API issues or questions:
1. Check the error message and correlation ID
2. Review backend logs at `/logs`
3. Open an issue on GitHub
4. Contact support (when implemented)