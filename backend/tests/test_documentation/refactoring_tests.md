# Refactoring Tests Documentation

## Overview

This document describes the tests for the new base classes and shared utilities being added as part of the backend refactoring effort to reduce code duplication.

## Test Files

### 1. test_base_service.py
Tests for the `BaseAzureService` abstract base class that all services will inherit from.

**What it tests:**
- Service initialization with Azure clients
- Error handling for initialization failures
- Processing with progress callbacks
- Health check functionality
- Azure error conversion
- Service information retrieval

**Key test cases:**
- `test_initialization` - Verifies service initializes correctly
- `test_initialization_failure` - Ensures proper error handling
- `test_process_with_progress` - Tests async processing with callbacks
- `test_health_check` - Validates health monitoring
- `test_handle_azure_error` - Tests Azure SDK error conversion

### 2. test_file_processor.py
Tests for the `FileProcessor` utility that provides unified file operations.

**What it tests:**
- File upload to blob storage
- File download from blob storage
- ZIP package creation
- Job file cleanup
- Temporary file management
- File existence checks

**Key test cases:**
- `test_save_upload_file` - Tests FastAPI file upload handling
- `test_download_from_blob` - Tests blob download functionality
- `test_create_results_zip` - Tests ZIP creation and upload
- `test_cleanup_job_files` - Tests job cleanup operations
- `test_cleanup_temp_file` - Tests temporary file cleanup
- `test_file_exists` - Tests file existence checking

## Running the Tests

### Run all refactoring tests:
```bash
python tests/run_new_tests.py
```

### Run with coverage:
```bash
python tests/run_new_tests.py --coverage
```

### Run individual test files:
```bash
# Test base service
pytest tests/test_base_service.py -v

# Test file processor
pytest tests/test_file_processor.py -v
```

### Run specific test:
```bash
pytest tests/test_base_service.py::TestBaseAzureService::test_initialization -v
```

## Test Strategy

### 1. Unit Tests
All new base classes and utilities have comprehensive unit tests with mocked dependencies.

### 2. Integration Points
Tests verify that new code integrates properly with existing utilities:
- FileHandler integration
- StorageService integration
- Azure client management
- Configuration system

### 3. Coverage Goals
- Minimum 90% coverage for new code
- All public methods tested
- Error paths covered
- Edge cases handled

## Mocking Strategy

### Azure Services
All Azure SDK clients are mocked to avoid real API calls:
```python
with patch('services.shared.file_processor.get_file_handler') as mock:
    handler = Mock()
    handler.zip_files = AsyncMock(return_value="/tmp/test.zip")
    mock.return_value = handler
```

### File Operations
File operations use temporary directories and are cleaned up after tests:
```python
fd, temp_path = tempfile.mkstemp()
os.write(fd, b"test content")
os.close(fd)
# ... test code ...
os.remove(temp_path)
```

## Test Markers

All tests are marked appropriately:
- `@pytest.mark.unit` - Unit tests
- `@pytest.mark.asyncio` - Async tests

## Future Tests

As we continue the refactoring, we'll add tests for:
1. `BaseAPIRouter` - Base class for API endpoints
2. `ResultPackager` - Standardized ZIP creation
3. `JobProcessor` - Common job processing patterns
4. Service migrations - As each service is refactored

## Validation

Before any existing code is modified:
1. Run existing tests to ensure they pass
2. Run new tests to ensure base classes work
3. Gradually migrate services with tests at each step