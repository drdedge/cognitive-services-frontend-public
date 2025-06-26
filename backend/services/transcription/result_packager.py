"""
Transcription result packager implementation.

Handles packaging of transcription results including multiple output formats,
speaker analysis, and detailed metadata.
"""
import os
import json
from typing import Dict, Any, List, Optional
from pathlib import Path

from services.shared.result_packager import ResultPackager
from utils.logging import get_logger

logger = get_logger(__name__)


class TranscriptionResultPackager(ResultPackager):
    """
    Result packager for Transcription service.
    
    Packages:
    - Multiple transcript formats (TXT, SRT, VTT, JSON)
    - Speaker diarization and analysis
    - Detailed metadata and statistics
    - Comprehensive summary reports
    """
    
    @property
    def service_name(self) -> str:
        """Get the service name."""
        return "transcription"
    
    async def _package_service_results(
        self, 
        temp_dir: str,
        results: Dict[str, Any],
        original_filename: str,
        metadata: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Package Transcription specific results.
        
        Args:
            temp_dir: Temporary directory for packaging
            results: Processing results containing transcripts, speaker data, etc.
            original_filename: Original audio filename
            metadata: Additional metadata
            
        Returns:
            Dictionary with packaging statistics
        """
        files = []
        stats = {
            "duration_seconds": results.get("duration", 0),
            "speakers_count": results.get("speakers_count", 0),
            "total_words": results.get("total_words", 0),
            "confidence_score": results.get("average_confidence", 0),
            "processing_time": metadata.get("processing_time", 0)
        }
        
        # Save original audio file if available
        if "original_file_path" in results and os.path.exists(results["original_file_path"]):
            dest_path = os.path.join(temp_dir, "original", original_filename)
            file_info = await self._copy_file(
                results["original_file_path"], 
                dest_path,
                "Original audio file"
            )
            files.append(file_info)
        
        # Save transcript in various formats
        base_name = Path(original_filename).stem
        
        # TXT format (primary transcript)
        if "transcript_text" in results:
            txt_path = os.path.join(
                temp_dir, 
                "processed", 
                f"{base_name}_transcript.txt"
            )
            file_info = await self._save_text_file(
                results["transcript_text"],
                txt_path,
                "Primary transcript with timestamps and speakers"
            )
            files.append(file_info)
            stats["transcript_size"] = file_info["size"]
        
        # SRT format (subtitles)
        if "transcript_srt" in results:
            srt_path = os.path.join(
                temp_dir,
                "processed",
                f"{base_name}_transcript.srt"
            )
            file_info = await self._save_text_file(
                results["transcript_srt"],
                srt_path,
                "Subtitle format (SRT)"
            )
            files.append(file_info)
        
        # VTT format (WebVTT)
        if "transcript_vtt" in results:
            vtt_path = os.path.join(
                temp_dir,
                "processed",
                f"{base_name}_transcript.vtt"
            )
            file_info = await self._save_text_file(
                results["transcript_vtt"],
                vtt_path,
                "WebVTT subtitle format"
            )
            files.append(file_info)
        
        # JSON format (detailed data)
        if "transcript_json" in results:
            json_path = os.path.join(
                temp_dir,
                "processed",
                f"{base_name}_transcript_detailed.json"
            )
            file_info = await self._save_json_file(
                results["transcript_json"],
                json_path,
                "Detailed transcript with word-level timing"
            )
            files.append(file_info)
        
        # Speaker analysis report
        if "speaker_analysis" in results:
            analysis_path = os.path.join(
                temp_dir,
                "reports",
                f"{base_name}_speaker_analysis.txt"
            )
            file_info = await self._save_text_file(
                results["speaker_analysis"],
                analysis_path,
                "Detailed speaker analysis and statistics"
            )
            files.append(file_info)
        
        # Transcript summary
        if "transcript_summary" in results:
            summary_path = os.path.join(
                temp_dir,
                "reports",
                f"{base_name}_transcript_summary.txt"
            )
            file_info = await self._save_text_file(
                results["transcript_summary"],
                summary_path,
                "Transcript summary and metadata"
            )
            files.append(file_info)
        
        # Create comprehensive analysis report
        analysis_report = self._create_analysis_report(results, stats)
        report_path = os.path.join(temp_dir, "reports", "transcription_analysis.json")
        file_info = await self._save_json_file(
            analysis_report,
            report_path,
            "Comprehensive transcription analysis"
        )
        files.append(file_info)
        
        # Save raw Azure response if available
        if "azure_response" in results:
            response_path = os.path.join(temp_dir, "metadata", "azure_speech_response.json")
            file_info = await self._save_json_file(
                results["azure_response"],
                response_path,
                "Raw Azure Speech Services response"
            )
            files.append(file_info)
        
        # Save speaker metadata
        if "speaker_metadata" in results:
            speaker_path = os.path.join(temp_dir, "metadata", "speaker_metadata.json")
            file_info = await self._save_json_file(
                results["speaker_metadata"],
                speaker_path,
                "Detailed speaker identification data"
            )
            files.append(file_info)
        
        stats["files_count"] = len(files)
        stats["files"] = files
        
        return stats
    
    def _create_analysis_report(
        self, 
        results: Dict[str, Any], 
        stats: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Create a comprehensive analysis report.
        
        Args:
            results: Processing results
            stats: Processing statistics
            
        Returns:
            Analysis report dictionary
        """
        report = {
            "transcription_summary": {
                "duration_seconds": stats["duration_seconds"],
                "duration_formatted": self._format_duration(stats["duration_seconds"]),
                "speakers_detected": stats["speakers_count"],
                "total_words": stats["total_words"],
                "average_confidence": round(stats["confidence_score"], 3),
                "processing_time_seconds": round(stats["processing_time"], 2)
            },
            "audio_properties": {
                "format": results.get("audio_format", "unknown"),
                "channels": results.get("audio_channels", 0),
                "sample_rate": results.get("sample_rate", 0),
                "bitrate": results.get("bitrate", 0)
            },
            "transcription_details": {
                "language": results.get("language", "en-US"),
                "model_used": results.get("model", "fast"),
                "features_enabled": {
                    "speaker_diarization": results.get("diarization_enabled", True),
                    "punctuation": results.get("punctuation_enabled", True),
                    "profanity_filter": results.get("profanity_filter", False)
                }
            }
        }
        
        # Add speaker statistics if available
        if "speaker_stats" in results:
            report["speaker_statistics"] = []
            for speaker_id, stats in results["speaker_stats"].items():
                report["speaker_statistics"].append({
                    "speaker": speaker_id,
                    "speaking_time_seconds": stats.get("speaking_time", 0),
                    "speaking_time_percentage": round(stats.get("percentage", 0), 1),
                    "words_spoken": stats.get("words", 0),
                    "phrases_count": stats.get("phrases", 0),
                    "average_confidence": round(stats.get("confidence", 0), 3)
                })
        
        # Add quality metrics if available
        if "quality_metrics" in results:
            report["quality_metrics"] = results["quality_metrics"]
        
        # Add warnings or issues
        if "warnings" in results:
            report["warnings"] = results["warnings"]
        
        return report
    
    def _format_duration(self, seconds: float) -> str:
        """
        Format duration in seconds to human-readable format.
        
        Args:
            seconds: Duration in seconds
            
        Returns:
            Formatted duration string (e.g., "1h 23m 45s")
        """
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        
        parts = []
        if hours > 0:
            parts.append(f"{hours}h")
        if minutes > 0:
            parts.append(f"{minutes}m")
        # Always show seconds if there are no hours, or if seconds is non-zero
        if (hours == 0 and minutes > 0) or secs > 0 or not parts:
            parts.append(f"{secs}s")
        
        return " ".join(parts)