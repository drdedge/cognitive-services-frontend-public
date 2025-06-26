# backend/services/document_intelligence/table_extractor.py
"""
Table extraction from Azure Document Intelligence – Multi-format output
======================================================================

This module specializes in extracting and converting tables from Azure Document
Intelligence results into multiple formats for flexible consumption:

## Key Features:
-----------------
- String-to-dict parsing for Azure SDK compatibility
- CSV generation with proper cell positioning
- Markdown table formatting for documentation
- Excel workbook creation with consolidation
- Multi-sheet organization by page and table
- Sanitized sheet naming for Excel compatibility

## Output Formats:
------------------
- Individual CSV files per table
- Markdown representation for inline display
- Excel workbook with consolidated view
- Metadata preservation (page numbers, dimensions)

The extractor handles various Azure response formats and ensures consistent
output regardless of the underlying SDK version or response structure.
"""
import ast
import io
import csv
import os
import pandas as pd
from typing import List, Dict, Tuple, Optional, Any

from utils.logging import get_logger
from services.shared.field_accessor import get_field

logger = get_logger(__name__)


def parse_string_to_dict(value: Any) -> Any:
    """
    Parse string representations of dictionaries/lists to actual objects.
    
    Args:
        value: Value that might be a string representation
        
    Returns:
        Parsed object or original value if not a string
    """
    if isinstance(value, str):
        # Check if it looks like a dict or list
        if (value.strip().startswith('{') or value.strip().startswith('[')):
            try:
                return ast.literal_eval(value)
            except (ValueError, SyntaxError) as e:
                logger.warning(f"Failed to parse string representation: {value[:100]}...")
                return value
    return value


async def process_tables(
    result, 
    doc_name: str, 
    file_ext: str,
    file_handler
) -> Tuple[List[str], List[str], List[Dict]]:
    """
    Process tables from document.
    
    Args:
        result: Azure Document Intelligence result
        doc_name: Document name without extension
        file_ext: File extension
        file_handler: File handler for saving files
        
    Returns:
        Tuple of (csv_files, markdown_tables, csv_files_info)
    """
    csv_files = []
    csv_files_info = []
    markdown_tables = []
    
    # Direct attribute access like in the working code
    if not hasattr(result, 'tables') or not result.tables:
        logger.info("No tables detected in the document.")
        return csv_files, markdown_tables, csv_files_info
    
    logger.info(f"Found {len(result.tables)} tables in document")
    
    for i, table in enumerate(result.tables):
        # Get page number - matching the working code pattern
        page_number = 1
        if hasattr(table, 'bounding_regions') and table.bounding_regions:
            page_number = table.bounding_regions[0].page_number if hasattr(table.bounding_regions[0], 'page_number') else 1
        elif isinstance(table, dict):
            # Fallback for dict-like tables
            page_number = table.get('boundingRegions', [{}])[0].get('pageNumber', 1)
        
        # Save table to CSV
        csv_path = await save_table_to_csv(
            table, doc_name, file_ext, i, page_number, file_handler
        )
        
        if csv_path:
            csv_files.append(csv_path)
            
            # Get row and column count
            if hasattr(table, 'row_count'):
                row_count = table.row_count or 0
                column_count = table.column_count or 0
            else:
                # Fallback for dict-like tables
                row_count = table.get('rowCount', 0) if isinstance(table, dict) else 0
                column_count = table.get('columnCount', 0) if isinstance(table, dict) else 0
            
            csv_files_info.append({
                "path": csv_path,
                "page_number": page_number,
                "table_index": i,
                "row_count": row_count,
                "column_count": column_count
            })
            
            # Convert to markdown
            markdown_table = table_to_markdown(table)
            if markdown_table:  # Only add non-empty tables
                markdown_tables.append(markdown_table)
    
    logger.info(f"Processed {len(csv_files)} tables from document")
    return csv_files, markdown_tables, csv_files_info


async def save_table_to_csv(
    table, 
    doc_name: str, 
    file_ext: str, 
    table_index: int,
    page_number: int,
    file_handler
) -> str:
    """Save a table to CSV file."""
    # Handle both object attributes and dict access for Azure SDK compatibility
    if hasattr(table, 'row_count'):
        rows = table.row_count or 0
        cols = table.column_count or 0
        cells = table.cells or []
    elif isinstance(table, dict):
        rows = table.get('rowCount', 0) or 0
        cols = table.get('columnCount', 0) or 0
        cells = table.get('cells', [])
    else:
        rows = 0
        cols = 0
        cells = []
    
    if rows == 0 or cols == 0:
        logger.warning(f"Table {table_index} has no rows or columns: rows={rows}, cols={cols}")
        return ""
    
    cells_matrix = [["" for _ in range(cols)] for _ in range(rows)]
    
    # Handle potential string representation of cells
    if isinstance(cells, str):
        cells = parse_string_to_dict(cells) or []
    
    for cell in cells:
        # Handle potential string representation of individual cells
        if isinstance(cell, str):
            cell = parse_string_to_dict(cell)
            if not isinstance(cell, dict):
                continue
        
        # Handle both object attributes and dict access
        if hasattr(cell, 'row_index'):
            row_idx = cell.row_index or 0
            col_idx = cell.column_index or 0
            content = cell.content or ""
        elif isinstance(cell, dict):
            row_idx = cell.get('rowIndex', 0) or 0
            col_idx = cell.get('columnIndex', 0) or 0
            content = cell.get('content', '') or ""
        else:
            continue
        
        if row_idx < rows and col_idx < cols:
            cells_matrix[row_idx][col_idx] = content
    
    # Create CSV filename
    csv_filename = f"{doc_name}_{file_ext}_page{page_number}_table{table_index}.csv"
    csv_content = io.StringIO()
    writer = csv.writer(csv_content)
    
    for row in cells_matrix:
        writer.writerow(row)
    
    # Save as temporary file
    csv_path = await file_handler.create_temp_file(
        csv_content.getvalue().encode('utf-8'),
        csv_filename
    )
    
    logger.info(f"Saved table {table_index} to {csv_path}")
    return csv_path


def table_to_markdown(table) -> str:
    """Convert table to markdown format."""
    # Handle both object attributes and dict access
    if hasattr(table, 'row_count'):
        rows = table.row_count or 0
        cols = table.column_count or 0
        cells = table.cells or []
    elif isinstance(table, dict):
        rows = table.get('rowCount', 0) or 0
        cols = table.get('columnCount', 0) or 0
        cells = table.get('cells', [])
    else:
        rows = 0
        cols = 0
        cells = []
    
    if rows == 0 or cols == 0:
        return ""
    
    # Create matrix
    cells_matrix = [["" for _ in range(cols)] for _ in range(rows)]
    
    # Handle potential string representation of cells
    if isinstance(cells, str):
        cells = parse_string_to_dict(cells) or []
    
    for cell in cells:
        # Handle potential string representation of individual cells
        if isinstance(cell, str):
            cell = parse_string_to_dict(cell)
            if not isinstance(cell, dict):
                continue
        
        # Handle both object attributes and dict access
        if hasattr(cell, 'row_index'):
            row_idx = cell.row_index or 0
            col_idx = cell.column_index or 0
            content = (cell.content or "").strip()
        elif isinstance(cell, dict):
            row_idx = cell.get('rowIndex', 0) or 0
            col_idx = cell.get('columnIndex', 0) or 0
            content = (cell.get('content', '') or "").strip()
        else:
            continue
        
        if row_idx < rows and col_idx < cols:
            cells_matrix[row_idx][col_idx] = content
    
    # Convert to markdown
    markdown_lines = []
    
    # Header row
    if rows > 0:
        markdown_lines.append("| " + " | ".join(cells_matrix[0]) + " |")
        markdown_lines.append("|" + "|".join(["---" for _ in range(cols)]) + "|")
    
    # Data rows
    for row in cells_matrix[1:]:
        markdown_lines.append("| " + " | ".join(row) + " |")
    
    return "\n".join(markdown_lines)


async def create_excel_from_tables(
    csv_files_info: List[Dict], 
    doc_name: str,
    file_handler
) -> Optional[str]:
    """Create Excel file with all tables and consolidated view."""
    if not csv_files_info:
        return None
    
    try:
        # Collect all dataframes and find max columns
        all_tables = []
        max_cols = 0
        
        for csv_info in csv_files_info:
            csv_path = csv_info.get("path", "")
            if os.path.exists(csv_path):
                try:
                    df = pd.read_csv(csv_path, header=None)
                    if not df.empty:
                        max_cols = max(max_cols, len(df.columns))
                        all_tables.append({
                            'df': df,
                            'page_number': csv_info.get("page_number", 1),
                            'table_index': csv_info.get("table_index", 0),
                            'tab_name': f"page{csv_info.get('page_number', 1):02d}_table{csv_info.get('table_index', 0):02d}"
                        })
                except Exception as e:
                    logger.error(f"Failed to read CSV {csv_path}: {str(e)}")
        
        if not all_tables:
            logger.warning("No valid tables found for Excel creation")
            return None
        
        # Create Excel file in memory
        excel_buffer = io.BytesIO()
        
        with pd.ExcelWriter(excel_buffer, engine='openpyxl') as writer:
            # Create consolidated sheet
            consolidated_rows = []
            
            for table_info in all_tables:
                df = table_info['df']
                tab_name = table_info['tab_name']
                
                # Ensure all tables have the same number of columns
                if len(df.columns) < max_cols:
                    for i in range(len(df.columns), max_cols):
                        df[i] = ''
                
                # Add header row with tab name
                header_row = [tab_name] + [''] * (max_cols - 1)
                consolidated_rows.append(header_row)
                
                # Add blank row
                consolidated_rows.append([''] * max_cols)
                
                # Add table data
                for _, row in df.iterrows():
                    consolidated_rows.append(row.tolist()[:max_cols])
                
                # Add blank row after table
                consolidated_rows.append([''] * max_cols)
            
            # Create consolidated dataframe
            col_names = [f'Column_{i+1}' for i in range(max_cols)]
            consolidated_df = pd.DataFrame(consolidated_rows, columns=col_names)
            
            # Write consolidated sheet first
            consolidated_df.to_excel(writer, sheet_name='consolidated', index=False)
            
            # Then write individual sheets
            for table_info in all_tables:
                df = table_info['df']
                tab_name = table_info['tab_name']
                
                # Write to individual sheet
                sanitized_tab_name = _sanitize_sheet_name(tab_name)
                df.to_excel(writer, sheet_name=sanitized_tab_name, index=False, header=False)
        
        excel_buffer.seek(0)
        excel_filename = f"{doc_name}_tables.xlsx"
        excel_path = await file_handler.create_temp_file(
            excel_buffer.read(),
            excel_filename
        )
        
        logger.info(f"Created Excel file with {len(all_tables)} tables: {excel_path}")
        return excel_path
        
    except Exception as e:
        logger.error(f"Failed to create Excel file: {str(e)}")
        return None


def _sanitize_sheet_name(name: str) -> str:
    """Sanitize sheet name for Excel compatibility."""
    # Remove or replace invalid characters
    invalid_chars = ['\\', '/', '*', '[', ']', ':', '?']
    for char in invalid_chars:
        name = name.replace(char, '_')
    
    # Truncate to 31 characters (Excel limit)
    if len(name) > 31:
        name = name[:31]
    
    return name.strip() or "Sheet1"