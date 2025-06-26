# backend/services/document_intelligence/processor.py
"""
Document processing logic for Azure Document Intelligence – Core extraction
==========================================================================

This module handles the extraction and processing of document content from Azure
Document Intelligence results. It provides functions for text extraction, confidence
analysis, and metadata processing:

## Key Features:
-----------------
- Text extraction with markdown formatting
- Table marker replacement with markdown tables
- Page-by-page content splitting
- Word-level confidence statistics
- Raw Azure response preservation
- Page metadata extraction

## Processing Components:
-------------------------
- Content extraction with formatting preservation
- Statistical analysis of confidence scores
- Page-level confidence aggregation
- Low-confidence page identification
- Response serialization for debugging

The processor integrates with the file handler for efficient temporary file
management and provides structured data for downstream consumption.
"""
import re
import os
import json
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime

from utils.logging import get_logger
from services.shared.field_accessor import get_field
from models.document_models import DocumentResults, TableData

logger = get_logger(__name__)


async def extract_text_content(
    result,
    markdown_tables: List[str],
    doc_name: str,
    file_ext: str,
    file_handler
) -> Tuple[Optional[str], List[str]]:
    """
    Extract text content from the document result.
    
    Args:
        result: Azure Document Intelligence result
        markdown_tables: List of markdown tables to insert
        doc_name: Document name without extension
        file_ext: File extension
        file_handler: File handler for saving files
        
    Returns:
        Tuple of (markdown_content, md_pages)
    """
    content = get_field(result, 'content', "")
    if not content:
        logger.warning("No content found in Azure response")
        return None, []
    
    logger.info(f"Extracted content length: {len(content)} characters")
    
    # Replace table markers with markdown tables
    if markdown_tables:
        table_pattern = re.compile(r"<table>.*?</table>", re.DOTALL)
        table_index = 0
        
        def replace_table(match):
            nonlocal table_index
            if table_index < len(markdown_tables):
                replacement = markdown_tables[table_index]
                table_index += 1
                return replacement
            return match.group(0)
        
        content = re.sub(table_pattern, replace_table, content)
    
    # Split into pages
    md_pages = []
    if content:
        pages = [p.strip() for p in content.split("<!-- PageBreak -->") if p.strip()]
        
        for i, page in enumerate(pages, start=1):
            page_filename = f"{doc_name}_{file_ext}_page{i}.md"
            page_path = await file_handler.create_temp_file(
                page.encode('utf-8'),
                page_filename
            )
            md_pages.append(page_path)
    
    return content, md_pages


def calculate_confidence_statistics(result) -> Dict[str, Any]:
    """Extract and calculate word-level confidence statistics from the document."""
    all_confidence_scores = []
    page_confidences = {}
    
    pages = get_field(result, 'pages', [])
    for page in pages:
        page_num = get_field(page, 'pageNumber', 1)
        words = get_field(page, 'words', [])
        
        if words:
            page_scores = []
            for word in words:
                confidence = get_field(word, 'confidence')
                if confidence is not None:
                    confidence_value = float(confidence)
                    all_confidence_scores.append(confidence_value)
                    page_scores.append(confidence_value)
            
            if page_scores:
                page_confidences[page_num] = page_scores
    
    # Calculate statistics
    stats = {
        "document_level": {},
        "page_level_summary": {},
        "low_confidence_pages": []
    }
    
    if all_confidence_scores:
        import numpy as np
        np_scores = np.array(all_confidence_scores)
        stats["document_level"] = {
            "mean": float(np.mean(np_scores)),
            "median": float(np.median(np_scores)),
            "std": float(np.std(np_scores)),
            "min": float(np.min(np_scores)),
            "max": float(np.max(np_scores)),
            "q1": float(np.percentile(np_scores, 25)),
            "q3": float(np.percentile(np_scores, 75)),
            "total_words": len(all_confidence_scores)
        }
        
        # Calculate page-level statistics
        page_averages = []
        for page_num, page_scores in sorted(page_confidences.items()):
            if page_scores:
                avg_confidence = np.mean(page_scores)
                page_averages.append(avg_confidence)
                
                # Track pages with average confidence below 0.85
                if avg_confidence < 0.85:
                    stats["low_confidence_pages"].append({
                        "page": page_num,
                        "average_confidence": float(avg_confidence),
                        "min_confidence": float(np.min(page_scores)),
                        "max_confidence": float(np.max(page_scores)),
                        "word_count": len(page_scores),
                        "words_below_85": sum(1 for score in page_scores if score < 0.85)
                    })
        
        # Summary of page-level averages
        if page_averages:
            stats["page_level_summary"] = {
                "total_pages": len(page_averages),
                "mean_page_confidence": float(np.mean(page_averages)),
                "min_page_confidence": float(np.min(page_averages)),
                "max_page_confidence": float(np.max(page_averages)),
                "pages_below_85": len(stats["low_confidence_pages"])
            }
    else:
        # No confidence scores found
        stats["document_level"] = {
            "mean": 0.0,
            "median": 0.0,
            "std": 0.0,
            "min": 0.0,
            "max": 0.0,
            "q1": 0.0,
            "q3": 0.0,
            "total_words": 0
        }
        stats["page_level_summary"] = {
            "total_pages": 0,
            "mean_page_confidence": 0.0,
            "min_page_confidence": 0.0,
            "max_page_confidence": 0.0,
            "pages_below_85": 0
        }
    
    return stats


async def save_raw_response(
    result, 
    doc_name: str, 
    job_id: str,
    file_handler
) -> Optional[str]:
    """Save the full raw Azure Document Intelligence response as JSON."""
    try:
        response_data = {
            "document_name": doc_name,
            "job_id": job_id,
            "timestamp": datetime.utcnow().isoformat(),
            "result_type": type(result).__name__
        }
        
        # Save the full result
        if hasattr(result, 'to_dict'):
            try:
                response_data["azure_response"] = result.to_dict()
            except Exception as e:
                logger.warning(f"Failed to convert result to dict: {e}")
                try:
                    response_data["azure_response"] = dict(result)
                except:
                    response_data["azure_response"] = str(result)
        else:
            try:
                response_data["azure_response"] = dict(result)
            except:
                response_data["azure_response"] = str(result)
        
        # Save as JSON
        json_filename = f"{doc_name}_azure_response.json"
        json_content = json.dumps(response_data, indent=2, default=str)
        
        json_path = await file_handler.create_temp_file(
            json_content.encode('utf-8'),
            json_filename
        )
        
        logger.info(f"Saved raw Azure response to: {json_path}")
        return json_path
        
    except Exception as e:
        logger.error(f"Failed to save raw Azure response: {str(e)}")
        return None


def extract_page_metadata(result) -> Tuple[List[Any], int]:
    """Extract page metadata from the result."""
    pages_data = []
    total_pages = 0
    
    pages = get_field(result, 'pages', [])
    if pages:
        total_pages = len(pages)
        
        # Just extract metadata for first 3 pages
        for page in pages[:3]:
            page_number = get_field(page, 'pageNumber', 1)
            width = get_field(page, 'width', 0)
            height = get_field(page, 'height', 0)
            text_angle = get_field(page, 'angle', 0.0)
            
            from models.document_models import PageData
            page_data = PageData(
                page_number=page_number,
                width=width,
                height=height,
                text_angle=text_angle,
                words=[],  # Don't include all words in response
                tables=[]
            )
            pages_data.append(page_data)
    
    return pages_data, total_pages


def create_table_data(csv_files_info: List[Dict]) -> List[TableData]:
    """Create TableData objects from CSV file info."""
    tables = []
    for info in csv_files_info:
        table = TableData(
            page_number=info.get("page_number", 1),
            table_index=info.get("table_index", 0),
            rows=info.get("row_count", 0),
            columns=info.get("column_count", 0),
            cells=[],  # Don't include full content in API response
            confidence=None
        )
        tables.append(table)
    return tables