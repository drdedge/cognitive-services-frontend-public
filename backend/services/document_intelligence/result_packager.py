"""
Document Intelligence result packager implementation.

Handles packaging of document analysis results including markdown content,
tables, confidence dashboards, and metadata.
"""
import os
import json
from typing import Dict, Any, List, Optional
from pathlib import Path

from services.shared.result_packager import ResultPackager
from utils.logging import get_logger

logger = get_logger(__name__)


class DocumentIntelligenceResultPackager(ResultPackager):
    """
    Result packager for Document Intelligence service.
    
    Packages:
    - Markdown content (full document and individual pages)
    - Extracted tables (CSV and Excel formats)
    - Confidence dashboard visualization
    - Analysis metadata and statistics
    """
    
    @property
    def service_name(self) -> str:
        """Get the service name."""
        return "document_intelligence"
    
    async def _package_service_results(
        self, 
        temp_dir: str,
        results: Dict[str, Any],
        original_filename: str,
        metadata: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Package Document Intelligence specific results.
        
        Args:
            temp_dir: Temporary directory for packaging
            results: Processing results containing markdown, tables, etc.
            original_filename: Original document filename
            metadata: Additional metadata
            
        Returns:
            Dictionary with packaging statistics
        """
        files = []
        stats = {
            "pages_count": results.get("pages_count", 0),
            "tables_count": results.get("tables_count", 0),
            "confidence_score": results.get("average_confidence", 0),
            "processing_time": metadata.get("processing_time", 0)
        }
        
        # Save original file if available
        if "original_file_path" in results and os.path.exists(results["original_file_path"]):
            dest_path = os.path.join(temp_dir, "original", original_filename)
            file_info = await self._copy_file(
                results["original_file_path"], 
                dest_path,
                "Original document"
            )
            files.append(file_info)
        
        # Save full markdown content
        if "markdown_content" in results:
            md_path = os.path.join(
                temp_dir, 
                "processed", 
                f"{Path(original_filename).stem}_document.md"
            )
            file_info = await self._save_text_file(
                results["markdown_content"],
                md_path,
                "Full document in markdown format"
            )
            files.append(file_info)
            stats["markdown_size"] = file_info["size"]
        
        # Save individual page markdown files
        if "page_markdowns" in results:
            pages_dir = os.path.join(temp_dir, "processed", "pages")
            os.makedirs(pages_dir, exist_ok=True)
            
            for page_num, page_content in enumerate(results["page_markdowns"], 1):
                page_path = os.path.join(
                    pages_dir,
                    f"{Path(original_filename).stem}_page{page_num}.md"
                )
                file_info = await self._save_text_file(
                    page_content,
                    page_path,
                    f"Page {page_num} markdown content"
                )
                files.append(file_info)
        
        # Save table CSV files
        if "table_csv_files" in results:
            csv_dir = os.path.join(temp_dir, "processed", "tables", "csv")
            os.makedirs(csv_dir, exist_ok=True)
            
            for csv_file in results["table_csv_files"]:
                if os.path.exists(csv_file["path"]):
                    dest_path = os.path.join(csv_dir, csv_file["filename"])
                    file_info = await self._copy_file(
                        csv_file["path"],
                        dest_path,
                        f"Table from page {csv_file.get('page', 'unknown')}"
                    )
                    files.append(file_info)
        
        # Save Excel file with all tables
        if "excel_file_path" in results and os.path.exists(results["excel_file_path"]):
            excel_path = os.path.join(
                temp_dir,
                "processed",
                f"{Path(original_filename).stem}_tables.xlsx"
            )
            file_info = await self._copy_file(
                results["excel_file_path"],
                excel_path,
                "All tables in Excel format"
            )
            files.append(file_info)
            stats["excel_file_size"] = file_info["size"]
        
        # Save confidence dashboard
        if "confidence_dashboard_path" in results and os.path.exists(results["confidence_dashboard_path"]):
            dashboard_path = os.path.join(
                temp_dir,
                "reports",
                "confidence_dashboard.png"
            )
            file_info = await self._copy_file(
                results["confidence_dashboard_path"],
                dashboard_path,
                "Confidence analysis visualization"
            )
            files.append(file_info)
        
        # Save analysis summary
        analysis_summary = self._create_analysis_summary(results, stats)
        summary_path = os.path.join(temp_dir, "reports", "analysis_summary.json")
        file_info = await self._save_json_file(
            analysis_summary,
            summary_path,
            "Detailed analysis summary"
        )
        files.append(file_info)
        
        # Save raw Azure response if available
        if "azure_response" in results:
            response_path = os.path.join(temp_dir, "metadata", "azure_response.json")
            file_info = await self._save_json_file(
                results["azure_response"],
                response_path,
                "Raw Azure Document Intelligence response"
            )
            files.append(file_info)
        
        # Save confidence statistics
        if "confidence_stats" in results:
            stats_path = os.path.join(temp_dir, "metadata", "confidence_statistics.json")
            file_info = await self._save_json_file(
                results["confidence_stats"],
                stats_path,
                "Detailed confidence statistics"
            )
            files.append(file_info)
        
        stats["files_count"] = len(files)
        stats["files"] = files
        
        return stats
    
    def _create_analysis_summary(
        self, 
        results: Dict[str, Any], 
        stats: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Create a human-readable analysis summary.
        
        Args:
            results: Processing results
            stats: Processing statistics
            
        Returns:
            Analysis summary dictionary
        """
        summary = {
            "document_analysis": {
                "pages_analyzed": stats["pages_count"],
                "tables_extracted": stats["tables_count"],
                "average_confidence": round(stats["confidence_score"], 3),
                "processing_time_seconds": round(stats["processing_time"], 2)
            },
            "content_statistics": {
                "total_characters": results.get("total_characters", 0),
                "total_words": results.get("total_words", 0),
                "total_lines": results.get("total_lines", 0)
            },
            "extraction_details": {
                "model_used": results.get("model_used", "prebuilt-layout"),
                "extraction_successful": results.get("extraction_successful", True),
                "warnings": results.get("warnings", [])
            }
        }
        
        # Add table details if available
        if "table_details" in results:
            summary["table_details"] = []
            for table in results["table_details"]:
                summary["table_details"].append({
                    "page": table.get("page", 0),
                    "rows": table.get("rows", 0),
                    "columns": table.get("columns", 0),
                    "cells": table.get("cells", 0),
                    "confidence": round(table.get("confidence", 0), 3)
                })
        
        # Add page-level statistics if available
        if "page_stats" in results:
            summary["page_statistics"] = results["page_stats"]
        
        return summary