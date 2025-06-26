# backend/services/document_intelligence/confidence_dashboard.py
"""
Confidence visualization dashboard with matplotlib – Statistical analysis
========================================================================

This module generates comprehensive visual dashboards for analyzing document
confidence scores from Azure Document Intelligence results:

## Key Features:
-----------------
- Document-level confidence box plots
- Page-by-page confidence analysis
- Confidence score distribution histograms
- Low-confidence page identification
- High-resolution PNG output
- Statistical summary overlays

## Visualization Components:
----------------------------
- Box plots with quartile analysis
- Distribution histograms with binning
- Bar charts for problematic pages
- Statistical annotations (mean, median)
- Professional styling with seaborn

The dashboard provides immediate visual insights into document quality and
helps identify pages that may require manual review or re-processing.
"""
import io
import numpy as np
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend
import matplotlib.pyplot as plt
import seaborn as sns
from typing import Dict, Any, Optional, List

from utils.logging import get_logger
from services.shared.field_accessor import get_field

logger = get_logger(__name__)


async def create_confidence_dashboard(
    result,
    doc_name: str,
    confidence_stats: Dict[str, Any],
    file_handler
) -> Optional[str]:
    """
    Create a confidence visualization dashboard.
    
    Args:
        result: Azure Document Intelligence result
        doc_name: Document name for the dashboard
        confidence_stats: Pre-calculated confidence statistics
        file_handler: File handler for saving the dashboard
        
    Returns:
        Path to the saved dashboard image or None
    """
    # Extract confidence scores by page
    page_confidences = {}
    all_confidence_scores = []
    
    pages = get_field(result, 'pages', [])
    if not pages:
        return None
        
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
    
    if not all_confidence_scores:
        logger.warning("No confidence scores found for dashboard generation")
        return None
    
    # Create the dashboard
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(16, 12))
    fig.tight_layout(pad=4.0)
    
    sns.set_style("whitegrid")
    
    # Chart 1: Document-Level Box Plot
    _create_document_boxplot(ax1, all_confidence_scores, confidence_stats)
    
    # Chart 2: Page-by-Page Confidence
    _create_page_confidence_plot(ax2, page_confidences)
    
    # Chart 3: Confidence Distribution Histogram
    _create_confidence_histogram(ax3, all_confidence_scores)
    
    # Chart 4: Low Confidence Pages
    _create_low_confidence_chart(ax4, confidence_stats)
    
    # Add overall title
    fig.suptitle(f'Confidence Analysis Dashboard - {doc_name}', fontsize=16, fontweight='bold', y=0.98)
    
    # Save the dashboard
    dashboard_filename = f"{doc_name}_confidence_dashboard.png"
    dashboard_content = io.BytesIO()
    plt.savefig(dashboard_content, format='png', dpi=300, bbox_inches='tight')
    plt.close()
    
    dashboard_content.seek(0)
    dashboard_path = await file_handler.create_temp_file(
        dashboard_content.read(),
        dashboard_filename
    )
    
    logger.info(f"Created confidence dashboard: {dashboard_path}")
    return dashboard_path


def _create_document_boxplot(ax, scores: List[float], stats: Dict[str, Any]):
    """Create document-level confidence box plot."""
    ax.boxplot(scores, vert=True, patch_artist=True,
               boxprops=dict(facecolor='lightblue', color='black'),
               medianprops=dict(color='red', linewidth=2),
               whiskerprops=dict(color='black'),
               capprops=dict(color='black'))
    ax.set_ylabel('Confidence Score')
    ax.set_title('Document-Level Word Confidence Distribution', fontsize=12, fontweight='bold')
    ax.set_ylim(0, 1.05)
    ax.grid(True, alpha=0.3)
    
    # Add statistics text
    mean_conf = stats["document_level"]["mean"]
    median_conf = stats["document_level"]["median"]
    ax.text(0.02, 0.98, f'Mean: {mean_conf:.3f}\nMedian: {median_conf:.3f}', 
            transform=ax.transAxes, verticalalignment='top',
            bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))


def _create_page_confidence_plot(ax, page_confidences: Dict[int, List[float]]):
    """Create page-by-page confidence box plots."""
    if not page_confidences:
        ax.text(0.5, 0.5, 'No page data available', 
                transform=ax.transAxes, ha='center', va='center')
        return
        
    sorted_pages = sorted(page_confidences.keys())[:20]  # Limit to 20 pages
    page_data = [page_confidences[p] for p in sorted_pages]
    
    if page_data:
        ax.boxplot(page_data, positions=range(1, len(sorted_pages) + 1), 
                   vert=True, patch_artist=True,
                   boxprops=dict(facecolor='lightgreen', color='black'),
                   medianprops=dict(color='red', linewidth=2))
        ax.set_xlabel('Page Number')
        ax.set_ylabel('Confidence Score')
        ax.set_title('Page-by-Page Word Confidence (First 20 Pages)', 
                     fontsize=12, fontweight='bold')
        ax.set_ylim(0, 1.05)
        ax.grid(True, alpha=0.3)


def _create_confidence_histogram(ax, scores: List[float]):
    """Create confidence score distribution histogram."""
    ax.hist(scores, bins=20, color='skyblue', edgecolor='black', alpha=0.7)
    ax.set_xlabel('Confidence Score')
    ax.set_ylabel('Word Count')
    ax.set_title('Confidence Score Distribution', fontsize=12, fontweight='bold')
    ax.grid(True, alpha=0.3)


def _create_low_confidence_chart(ax, stats: Dict[str, Any]):
    """Create bar chart of pages with low confidence."""
    low_conf_pages = stats.get("low_confidence_pages", [])
    
    if not low_conf_pages:
        ax.text(0.5, 0.5, 'No pages with low confidence\n(all pages have avg confidence ≥ 0.85)',
                transform=ax.transAxes, ha='center', va='center',
                fontsize=14, bbox=dict(boxstyle='round', facecolor='lightgreen', alpha=0.5))
        ax.set_title('Low Confidence Pages', fontsize=12, fontweight='bold')
        return
    
    # Sort by average confidence and take worst 10
    low_conf_pages.sort(key=lambda x: x["average_confidence"])
    worst_pages = low_conf_pages[:10]
    
    pages = [p["page"] for p in worst_pages]
    avg_confs = [p["average_confidence"] for p in worst_pages]
    
    bars = ax.bar(range(len(pages)), avg_confs, color='salmon', edgecolor='black')
    ax.set_xlabel('Page Number')
    ax.set_ylabel('Average Confidence')
    ax.set_title('Top 10 Pages with Lowest Average Confidence', 
                 fontsize=12, fontweight='bold')
    ax.set_xticks(range(len(pages)))
    ax.set_xticklabels([str(p) for p in pages])
    ax.set_ylim(0, 1)
    ax.grid(True, alpha=0.3, axis='y')
    
    # Add value labels
    for bar, conf in zip(bars, avg_confs):
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height,
                f'{conf:.3f}', ha='center', va='bottom', fontsize=9)