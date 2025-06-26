# Backend Test Suite

This directory contains a comprehensive test suite for the Cognitive Services Frontend backend, implementing a test-first development approach to guide implementation.

## Test Structure

```
tests/
├── conftest.py                 # Pytest configuration and shared fixtures
├── pytest.ini                 # Pytest settings and markers
├── test_api_endpoints.py       # API endpoint tests
├── test_services.py           # Business logic service tests
├── test_azure_integration.py  # Azure service integration tests
├── test_azure_storage.py       # Azure Blob Storage specific tests
├── test_websocket.py          # WebSocket functionality tests
├── test_file_handling.py      # File operations tests
├── test_infrastructure.py     # Infrastructure and configuration tests
├── test_integration.py        # End-to-end integration tests
├── test_translation_endpoint.py # Translation service endpoint tests
├── test_transcription_endpoint.py # Transcription service endpoint tests
├── fixtures/                  # Test fixtures and sample data
│   ├── sample_data.py         # Sample test data
│   └── azure_mocks.py         # Azure service mocks
├── utilities/                 # Test utilities and helper scripts
│   ├── validate_integration.py # Frontend-backend integration validator
│   └── run_tests.py           # Test runner with coverage options
└── README.md                  # This file
```

## Test Categories

### 1. API Endpoint Tests (`test_api_endpoints.py`)
- Document Intelligence endpoints
- Translation endpoints  
- Transcription endpoints
- Common endpoints (health, CORS, auth)
- Error handling and validation

### 2. Service Layer Tests (`test_services.py`)
- Document Intelligence service
- Translation service
- Transcription service
- Cost calculation service
- Job management service

### 3. Azure Integration Tests (`test_azure_integration.py`)
- Azure Blob Storage operations
- Document Intelligence API calls
- Translator API integration
- Speech Service integration
- Authentication and security

### 4. WebSocket Tests (`test_websocket.py`)
- Connection management
- Real-time messaging
- Error handling and recovery
- Integration with services
- Performance and scaling

### 5. File Handling Tests (`test_file_handling.py`)
- File upload validation
- Processing pipelines
- Storage operations
- Metadata handling
- Result packaging

### 6. Infrastructure Tests (`test_infrastructure.py`)
- Configuration loading and validation
- Environment variable handling
- Service initialization
- Dependency injection
- Health check endpoints

### 7. Integration Tests (`test_integration.py`)
- Full end-to-end workflows
- Multi-service interactions
- Real Azure service integration (when enabled)
- Performance under load
- Error recovery scenarios

### 8. Service-Specific Tests
- **Translation Endpoint Tests** (`test_translation_endpoint.py`): Comprehensive translation API testing
- **Transcription Endpoint Tests** (`test_transcription_endpoint.py`): Audio transcription API testing
- **Azure Storage Tests** (`test_azure_storage.py`): Blob storage operations and edge cases

## Test Fixtures and Mocks

### Sample Data (`fixtures/sample_data.py`)
Provides realistic test data including:
- Document analysis results
- Translation outputs
- Transcription results
- Error scenarios
- Cost calculations
- WebSocket messages

### Azure Mocks (`fixtures/azure_mocks.py`)
Comprehensive mocks for Azure services:
- `MockDocumentIntelligenceClient`
- `MockTranslatorClient`
- `MockSpeechServiceClient`
- `MockBlobStorageClient`

## Running Tests

### Prerequisites
```bash
# Install test dependencies
pip install -r requirements-test.txt
```

### Basic Test Execution
```bash
# Run all tests
pytest

# Run specific test file
pytest tests/test_api_endpoints.py

# Run specific test class
pytest tests/test_services.py::TestDocumentIntelligenceService

# Run specific test method
pytest tests/test_api_endpoints.py::TestDocumentIntelligenceEndpoints::test_process_document_success
```

### Test Categories
```bash
# Run only unit tests
pytest -m unit

# Run integration tests
pytest -m integration

# Run Azure service tests
pytest -m azure

# Run WebSocket tests
pytest -m websocket

# Run file handling tests
pytest -m file_upload

# Run performance tests
pytest -m performance
```

### Coverage and Reporting
```bash
# Run tests with coverage
pytest --cov=backend --cov-report=html

# Generate HTML coverage report
pytest --cov=backend --cov-report=html:htmlcov

# Generate JSON test report
pytest --json-report --json-report-file=test-report.json

# Generate HTML test report
pytest --html=test-report.html --self-contained-html
```

### Parallel Execution
```bash
# Run tests in parallel (faster execution)
pytest -n auto

# Run tests in parallel with specific worker count
pytest -n 4
```

## Test Markers

The test suite uses pytest markers to categorize tests:

- `@pytest.mark.unit` - Unit tests (fast, isolated)
- `@pytest.mark.integration` - Integration tests  
- `@pytest.mark.e2e` - End-to-end tests
- `@pytest.mark.slow` - Slow running tests (>5 seconds)
- `@pytest.mark.azure` - Tests requiring Azure services
- `@pytest.mark.websocket` - WebSocket functionality tests
- `@pytest.mark.file_upload` - File upload and processing tests
- `@pytest.mark.security` - Security-related tests
- `@pytest.mark.performance` - Performance and load tests

## Test Data Requirements

The tests expect specific sample files in the test fixtures:
- PDF documents (various sizes and complexities)
- DOCX documents with tables and formatting
- Audio files (WAV, MP3) of different lengths
- Text files for translation testing

Sample files are automatically created by the `sample_files` fixture in `conftest.py`.

## Environment Variables

Tests use environment variables for configuration:
```bash
TESTING=true
AZURE_DOC_INTELLIGENCE_ENDPOINT=https://test-doc.cognitiveservices.azure.com
AZURE_DOC_INTELLIGENCE_KEY=test-doc-key
AZURE_TRANSLATOR_ENDPOINT=https://test-translator.cognitiveservices.azure.com
AZURE_TRANSLATOR_KEY=test-translator-key
AZURE_SPEECH_ENDPOINT=https://test-speech.cognitiveservices.azure.com
AZURE_SPEECH_KEY=test-speech-key
AZURE_STORAGE_CONNECTION_STRING=DefaultEndpointsProtocol=https;AccountName=test;AccountKey=test-key;EndpointSuffix=core.windows.net
AZURE_STORAGE_CONTAINER=test-container
```

## Performance Benchmarks

The test suite includes performance benchmarks to ensure:
- API response times < 200ms (p95)
- File upload handling < 2s for 10MB files
- WebSocket message delivery < 100ms
- Memory usage < 200MB per session
- Support for 100 concurrent connections

## Test-Driven Development Workflow

1. **Write Tests First**: Before implementing a feature, write comprehensive tests that define the expected behavior
2. **Run Tests**: Execute tests to see them fail (red phase)
3. **Implement Code**: Write minimal code to make tests pass (green phase)  
4. **Refactor**: Improve code while keeping tests passing (refactor phase)
5. **Iterate**: Repeat for each feature or component

## Continuous Integration

The test suite is designed to run in CI/CD pipelines:
- All tests must pass before merging
- Minimum 80% code coverage required
- Performance benchmarks must be met
- Security tests must pass

## Test Data Security

- No real API keys or sensitive data in tests
- All test data is synthetic/mocked
- Temporary files are automatically cleaned up
- Azure service calls are mocked by default

## Test Utilities

The `utilities/` directory contains helper scripts for testing and validation:

### Integration Validator (`utilities/validate_integration.py`)
Validates that frontend and backend are properly integrated:
```bash
# Run from project root
python backend/tests/utilities/validate_integration.py
```

This script checks:
- Frontend service files exist and match backend endpoints
- WebSocket configuration is correct
- CORS is properly configured
- Error handling is consistent
- All required configuration files are present

### Test Runner (`utilities/run_tests.py`)
Enhanced test runner with coverage and reporting options:
```bash
# Run all tests
python backend/tests/utilities/run_tests.py

# Run with coverage
python backend/tests/utilities/run_tests.py --coverage

# Run specific test file
python backend/tests/utilities/run_tests.py test_translation_endpoint.py
```

## Troubleshooting

### Common Issues

1. **Import Errors**: Ensure the backend module is in Python path
2. **Async Test Failures**: Make sure to use `@pytest.mark.asyncio` for async tests
3. **Mock Issues**: Verify mock patches target the correct import paths
4. **File Permission Errors**: Ensure test directories are writable
5. **Memory Issues**: Use `pytest-xdist` for parallel execution to reduce memory usage

### Debug Mode
```bash
# Run tests with debug output
pytest -vv --tb=long

# Run single test with debugging
pytest tests/test_api_endpoints.py::test_specific_function -vv --pdb
```

This comprehensive test suite ensures high code quality and provides confidence in the backend implementation while following test-driven development principles.