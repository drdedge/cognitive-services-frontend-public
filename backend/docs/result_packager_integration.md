# ResultPackager Integration Guide

## Overview

The ResultPackager system provides a consistent way to package processing results across all cognitive services (Document Intelligence, Translation, and Transcription). This guide explains how to integrate the ResultPackager into existing services.

## Architecture

### Base Class: `ResultPackager`
Located in `/services/shared/result_packager.py`, provides:
- Standard directory structure creation
- File operation utilities (JSON, text, binary)
- ZIP packaging and blob storage upload
- Comprehensive error handling and cleanup

### Service-Specific Implementations
- `DocumentIntelligenceResultPackager`: Packages markdown, tables, confidence dashboards
- `TranslationResultPackager`: Packages translations, language detection, reports
- `TranscriptionResultPackager`: Packages transcripts, speaker analysis, multiple formats

## Standard Package Structure

All services produce ZIP files with this structure:
```
{job_id}_{service}_results.zip
├── original/          # Original input files
├── processed/         # Service outputs (main results)
├── metadata/          # JSON metadata and raw responses
├── reports/           # Human-readable reports
└── summary.json       # Package summary with statistics
```

## Integration Steps

### 1. Import the ResultPackager

```python
from services.document_intelligence.result_packager import DocumentIntelligenceResultPackager
# or
from services.translation.result_packager import TranslationResultPackager
# or
from services.transcription.result_packager import TranscriptionResultPackager
```

### 2. Initialize with FileHandler

```python
from utils.file_handler import FileHandler

# In your service class
self.file_handler = FileHandler()
self.result_packager = DocumentIntelligenceResultPackager(self.file_handler)
```

### 3. Prepare Results Dictionary

The results dictionary should contain all outputs from your service processing:

#### Document Intelligence Example:
```python
results = {
    "markdown_content": full_document_markdown,
    "page_markdowns": [page1_md, page2_md, ...],
    "pages_count": len(pages),
    "tables_count": len(tables),
    "average_confidence": 0.95,
    "table_csv_files": [
        {"path": "/tmp/table1.csv", "filename": "table1.csv", "page": 1}
    ],
    "excel_file_path": "/tmp/all_tables.xlsx",
    "confidence_dashboard_path": "/tmp/dashboard.png",
    "azure_response": raw_azure_response,
    "confidence_stats": {...},
    # Additional fields as needed
}
```

#### Translation Example:
```python
results = {
    "type": "document",  # or "text"
    "original_file_path": "/tmp/original.docx",
    "translated_file_path": "/tmp/translated.docx",
    "original_text": "Original content...",
    "translated_text": "Translated content...",
    "source_language": "en",
    "target_language": "es",
    "detected_language": "en",
    "characters_count": 1500,
    "language_detection": {...},
    "azure_response": {...}
}
```

#### Transcription Example:
```python
results = {
    "transcript_text": formatted_transcript,
    "transcript_srt": srt_content,
    "transcript_vtt": vtt_content,
    "transcript_json": detailed_json,
    "speaker_analysis": analysis_report,
    "duration": 120.5,
    "speakers_count": 2,
    "speaker_stats": {...},
    "azure_response": {...}
}
```

### 4. Create Metadata Dictionary

```python
metadata = {
    "processing_time": processing_duration,
    "job_id": job_id,
    "user": user_id,
    "timestamp": datetime.utcnow().isoformat(),
    # Service-specific options
    "model": "prebuilt-layout",
    "language": "en-US",
    # etc.
}
```

### 5. Call create_package()

```python
download_url = await self.result_packager.create_package(
    job_id=job_id,
    results=results,
    original_filename=original_filename,
    metadata=metadata
)
```

### 6. Return or Store the Download URL

```python
# Update job with download URL
await job_manager.update_job_result(job_id, download_url)

# Return to API
return {
    "job_id": job_id,
    "status": "completed",
    "download_url": download_url
}
```

## Complete Integration Example

### Before (Current Implementation):
```python
# In document_intelligence/service.py
async def create_results_package(self, job_id: str, results: dict) -> str:
    """Current packaging logic - scattered and service-specific."""
    try:
        # Create temp directory
        output_dir = f"/tmp/{job_id}_output"
        os.makedirs(output_dir, exist_ok=True)
        
        # Save markdown
        with open(f"{output_dir}/document.md", 'w') as f:
            f.write(results['markdown'])
        
        # Save tables
        for table in results['tables']:
            # ... save logic
        
        # Create ZIP manually
        zip_path = f"/tmp/{job_id}.zip"
        shutil.make_archive(zip_path.replace('.zip', ''), 'zip', output_dir)
        
        # Upload to blob
        blob_path = f"results/{job_id}/results.zip"
        download_url = await self.storage_service.upload_file(zip_path, blob_path)
        
        # Cleanup
        shutil.rmtree(output_dir)
        os.remove(zip_path)
        
        return download_url
        
    except Exception as e:
        logger.error(f"Failed to create package: {e}")
        raise
```

### After (With ResultPackager):
```python
# In document_intelligence/service.py
async def analyze_document(self, file_path: str, job_id: str, options: dict) -> str:
    """Process document and package results."""
    try:
        # ... existing processing logic ...
        
        # Prepare results for packager
        results = {
            "markdown_content": markdown_result,
            "page_markdowns": page_results,
            "pages_count": len(pages),
            "tables_count": len(tables),
            "average_confidence": confidence_stats['mean'],
            "table_csv_files": csv_files,
            "excel_file_path": excel_path,
            "confidence_dashboard_path": dashboard_path,
            "azure_response": raw_response,
            "confidence_stats": confidence_stats,
            "total_characters": char_count,
            "total_words": word_count,
            "model_used": options.get('model', 'prebuilt-layout')
        }
        
        metadata = {
            "processing_time": processing_time,
            "job_id": job_id,
            "options": options
        }
        
        # Create package with one line
        download_url = await self.result_packager.create_package(
            job_id, results, original_filename, metadata
        )
        
        return download_url
        
    except Exception as e:
        logger.error(f"Document processing failed: {e}")
        raise
```

## Benefits

1. **Consistency**: All services produce packages with the same structure
2. **Maintainability**: Packaging logic in one place
3. **Error Handling**: Automatic cleanup on errors
4. **Extensibility**: Easy to add new file types or reports
5. **Testing**: Centralized testing of packaging logic

## Testing

### Unit Tests
```python
# Test the packager in isolation
async def test_document_packager():
    mock_file_handler = Mock()
    packager = DocumentIntelligenceResultPackager(mock_file_handler)
    
    results = {...}  # Mock results
    download_url = await packager.create_package(
        "test-job", results, "test.pdf", {}
    )
    
    assert download_url is not None
    mock_file_handler.upload_to_blob.assert_called_once()
```

### Integration Tests
```python
# Test with real file operations
async def test_full_packaging_flow():
    file_handler = FileHandler()
    packager = DocumentIntelligenceResultPackager(file_handler)
    
    # Create real test files
    # Package them
    # Verify ZIP contents
```

## Migration Checklist

When migrating a service to use ResultPackager:

- [ ] Import the appropriate ResultPackager class
- [ ] Initialize packager with FileHandler
- [ ] Map current results to ResultPackager format
- [ ] Replace manual packaging code with `create_package()` call
- [ ] Update tests to verify new packaging
- [ ] Test ZIP contents match expected structure
- [ ] Verify frontend can still download and use packages
- [ ] Remove old packaging code
- [ ] Update service documentation

## Troubleshooting

### Common Issues

1. **Missing files in package**
   - Ensure all file paths in results dictionary exist
   - Check that files haven't been cleaned up prematurely

2. **Upload failures**
   - Verify FileHandler has correct Azure credentials
   - Check blob storage container exists
   - Ensure adequate permissions

3. **Memory issues with large files**
   - ResultPackager uses file operations, not memory
   - Ensure sufficient disk space in /tmp

4. **Unicode errors**
   - All text files are saved with UTF-8 encoding
   - JSON files use `ensure_ascii=False`

### Debug Tips

Enable detailed logging:
```python
import logging
logging.getLogger('services.shared.result_packager').setLevel(logging.DEBUG)
```

Inspect package contents without upload:
```python
# Temporarily modify upload_to_blob to save locally
async def debug_upload(zip_path, blob_path):
    shutil.copy(zip_path, f"/tmp/debug_{os.path.basename(zip_path)}")
    return "file:///tmp/debug_" + os.path.basename(zip_path)
```

## Future Enhancements

1. **Compression options**: Allow different compression levels
2. **Encryption**: Add optional password protection
3. **Streaming**: Support streaming large files directly to blob
4. **Versioning**: Track package format versions
5. **Partial packages**: Allow incremental result packaging