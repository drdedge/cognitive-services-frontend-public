# Services Layer Documentation

## Overview
Business logic layer that interfaces with Azure Cognitive Services and manages file operations.

## Service Architecture

### Base Service Pattern
All services should follow this pattern:
```python
class BaseService:
    def __init__(self, config: ServiceConfig):
        self.config = config
        self.client = self._initialize_client()
    
    async def process(self, input_data: Any) -> Result:
        # Validate input
        # Process with Azure service
        # Handle errors
        # Return structured result
```

## Service Implementations

### DocumentIntelligenceService
- **Purpose**: Wrapper around existing `az_doc_intelligence_processor.py`
- **Key Methods**:
  - `process_document(file: UploadFile) -> JobResult`
  - `get_page_count(file: bytes) -> int`
  - `extract_tables(result: AnalyzeResult) -> List[Table]`
- **Integration**: Uses existing processor with async wrapper

### TranslationService
- **Purpose**: Document and text translation using Azure Translator
- **Key Methods**:
  - `translate_text(text: str, source_lang: str, target_lang: str) -> TranslationResult`
  - `translate_document(file: bytes, target_lang: str) -> bytes`
  - `detect_language(text: str) -> str`
  - `get_supported_languages() -> Dict[str, List[str]]`

### TranscriptionService
- **Purpose**: Audio to text conversion using Azure Speech Service
- **Key Methods**:
  - `transcribe_audio(file: bytes, options: TranscriptionOptions) -> TranscriptionResult`
  - `get_audio_duration(file: bytes) -> float`
  - `format_transcript(result: SpeechResult, format: str) -> str`

### StorageService
- **Purpose**: Azure Blob Storage operations
- **Key Methods**:
  - `upload_file(file: bytes, path: str) -> str`
  - `download_file(blob_path: str) -> bytes`
  - `generate_sas_url(blob_path: str, expiry_hours: int) -> str`
  - `delete_old_files(days: int) -> int`
- **Directory Structure**:
  ```
  cognitive-services/
  ├── jobs/
  │   ├── {job_id}/
  │   │   ├── input/
  │   │   ├── output/
  │   │   └── logs/
  ```

### CostCalculatorService
- **Purpose**: Calculate processing costs based on Azure pricing
- **Pricing Models**:
  - Document Intelligence: $1.50 per page
  - Translation: $10 per million characters
  - Transcription: $1 per audio hour
- **Key Methods**:
  - `calculate_document_cost(pages: int) -> Decimal`
  - `calculate_translation_cost(characters: int) -> Decimal`
  - `calculate_transcription_cost(duration_seconds: float) -> Decimal`

## Error Handling

### Service Exceptions
```python
class ServiceException(Exception):
    def __init__(self, code: str, message: str, details: Dict = None):
        self.code = code
        self.message = message
        self.details = details or {}

class AzureServiceException(ServiceException):
    """Azure API errors"""

class ValidationException(ServiceException):
    """Input validation errors"""

class StorageException(ServiceException):
    """Storage operation errors"""
```

## Testing Services

### Mock Azure Responses
```python
@pytest.fixture
def mock_document_intelligence_client():
    # Return mock client with predefined responses
    pass

async def test_process_document(mock_client):
    service = DocumentIntelligenceService(mock_client)
    result = await service.process_document(test_file)
    assert result.status == "completed"
```

## Performance Considerations

### Async Operations
- All I/O operations should be async
- Use connection pooling for Azure clients
- Implement request queuing for rate limiting

### Caching
- Cache language lists (TTL: 24 hours)
- Cache cost calculations (TTL: 1 hour)
- Cache processed results (TTL: configurable)

## Security

### Input Validation
- File type validation before processing
- Size limits enforcement
- Content scanning for malicious files

### Secrets Management
- Never log API keys or sensitive data
- Use environment variables for configuration
- Implement key rotation support