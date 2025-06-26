#backend/services/transcription/output_generator.py
"""
Transcript output generator with multiple format support
=======================================================

Generates comprehensive output packages for transcription results, creating multiple
file formats and detailed analysis reports in a structured ZIP package:

## Key Features:
----------------
- Multiple output formats (TXT, JSON, SRT, VTT)
- Formatted transcript with timestamps and speakers
- Detailed speaker analysis reports
- Summary statistics and metadata
- Clean ZIP package organization
- Automatic file cleanup
- UTF-8 encoding for all text files

## Output Files Generated:
-------------------------
- Main transcript with timestamps and speakers
- Detailed JSON with full Azure response
- Summary statistics report
- SRT subtitle file
- WebVTT subtitle file
- Speaker analysis report

"""

import os
import json
import zipfile
import tempfile
from typing import Dict, Any, List
from datetime import datetime
from pathlib import Path

from utils.file_handler import get_file_handler
from utils.logging import get_logger

logger = get_logger(__name__)


class TranscriptOutputGenerator:
    """Generates output files for transcription results."""
    
    def __init__(self):
        """Initialize the output generator."""
        self.file_handler = get_file_handler()
    
    async def create_results_package(
        self,
        job_id: str,
        processed_data: Dict[str, Any],
        original_filename: str
    ) -> str:
        """
        Create a ZIP package with all transcription results.
        
        Args:
            job_id: Job identifier
            processed_data: Processed transcription data
            original_filename: Original audio file name
            
        Returns:
            Path to the created ZIP file in storage
        """
        try:
            # Create temp directory for output files - Windows compatible
            temp_dir = Path(tempfile.mkdtemp(prefix=f"{job_id}_outputs_"))
            
            # Extract base name without extension
            base_name = Path(original_filename).stem
            
            # Generate all output files
            files_created = []
            
            # 1. Main transcript with timestamps and speakers
            transcript_path = await self._create_transcript_file(
                temp_dir, base_name, processed_data
            )
            files_created.append(transcript_path)
            
            # 2. Detailed JSON with full Azure response
            json_path = await self._create_json_file(
                temp_dir, base_name, processed_data
            )
            files_created.append(json_path)
            
            # 3. Summary statistics
            summary_path = await self._create_summary_file(
                temp_dir, base_name, processed_data
            )
            files_created.append(summary_path)
            
            # 4. SRT subtitles
            srt_path = await self._create_srt_file(
                temp_dir, base_name, processed_data
            )
            files_created.append(srt_path)
            
            # 5. WebVTT subtitles
            vtt_path = await self._create_vtt_file(
                temp_dir, base_name, processed_data
            )
            files_created.append(vtt_path)
            
            # 6. Speaker analysis
            speaker_path = await self._create_speaker_analysis_file(
                temp_dir, base_name, processed_data
            )
            files_created.append(speaker_path)
            
            # Create ZIP file
            zip_filename = f"{job_id}_transcription_results.zip"
            zip_path = await self.file_handler.zip_files(
                files_created,
                zip_filename,
                job_id
            )
            
            # Cleanup temp files
            for file_path in files_created:
                try:
                    if os.path.exists(file_path):
                        os.remove(file_path)
                except Exception as e:
                    logger.debug(f"Could not remove temp file {file_path}: {e}")
            
            try:
                if temp_dir.exists():
                    temp_dir.rmdir()
            except Exception as e:
                logger.debug(f"Could not remove temp directory {temp_dir}: {e}")
            
            logger.info(f"Created transcription results package: {zip_filename}")
            return zip_path
            
        except Exception as e:
            logger.error(f"Error creating results package: {e}")
            raise
    
    async def _create_transcript_file(
        self,
        output_dir: Path,
        base_name: str,
        data: Dict[str, Any]
    ) -> str:
        """Create formatted transcript file with timestamps and speakers."""
        content_lines = [
            f"Transcript: {base_name}",
            f"Duration: {data['duration_formatted']}",
            f"Processed: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}",
            "=" * 80,
            ""
        ]
        
        # Add chunked transcript
        for chunk in data['chunked_transcript']:
            content_lines.append(chunk['formatted_text'])
            content_lines.append("")  # Empty line between chunks
        
        # Add statistics at the end
        content_lines.extend([
            "",
            "=" * 80,
            "STATISTICS",
            "=" * 80,
            f"Total Words: {data['statistics']['total_words']}",
            f"Total Phrases: {data['statistics']['total_phrases']}",
            f"Average Confidence: {data['statistics']['average_confidence']:.2%}",
            f"Words Per Minute: {data['statistics']['words_per_minute']}",
            f"Number of Speakers: {len(data['speakers'])}"
        ])
        
        content = "\n".join(content_lines)
        file_path = output_dir / f"{base_name}_transcript.txt"
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        return str(file_path)
    
    async def _create_json_file(
        self,
        output_dir: Path,
        base_name: str,
        data: Dict[str, Any]
    ) -> str:
        """Create detailed JSON file with full transcription data."""
        # Create a clean copy without internal processing data
        json_data = {
            'metadata': data.get('metadata', {}),
            'duration': {
                'milliseconds': data['duration_ms'],
                'formatted': data['duration_formatted']
            },
            'statistics': data['statistics'],
            'speakers': data['speakers'],
            'combined_text': data['combined_text'],
            'chunked_transcript': [
                {
                    'chunk_number': chunk['chunk_number'],
                    'start_time': chunk['start_time'],
                    'end_time': chunk['end_time'],
                    'duration_ms': chunk['duration_ms'],
                    'speakers': chunk['speakers'],
                    'text': chunk['formatted_text']
                }
                for chunk in data['chunked_transcript']
            ],
            'phrases': data['phrases']
        }
        
        file_path = output_dir / f"{base_name}_transcript_detailed.json"
        
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(json_data, f, indent=2, ensure_ascii=False)
        
        return str(file_path)
    
    async def _create_summary_file(
        self,
        output_dir: Path,
        base_name: str,
        data: Dict[str, Any]
    ) -> str:
        """Create summary file with key statistics and metadata."""
        content_lines = [
            f"TRANSCRIPTION SUMMARY",
            f"====================",
            f"",
            f"File: {base_name}",
            f"Processed: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}",
            f"",
            f"AUDIO INFORMATION",
            f"-----------------",
            f"Duration: {data['duration_formatted']}",
            f"Language: {data['metadata'].get('language', 'Unknown')}",
            f"",
            f"TRANSCRIPTION STATISTICS",
            f"------------------------",
            f"Total Words: {data['statistics']['total_words']:,}",
            f"Total Phrases: {data['statistics']['total_phrases']:,}",
            f"Words Per Minute: {data['statistics']['words_per_minute']}",
            f"Average Confidence: {data['statistics']['average_confidence']:.2%}",
            f"",
            f"SPEAKER ANALYSIS",
            f"----------------",
            f"Total Speakers: {len(data['speakers'])}"
        ]
        
        # Add speaker details
        for speaker_id, speaker_info in sorted(data['speakers'].items()):
            content_lines.extend([
                f"",
                f"Speaker {speaker_id}:",
                f"  - Speaking Time: {speaker_info['total_duration_ms'] / 1000:.1f}s ({speaker_info['speaking_percentage']:.1f}%)",
                f"  - Word Count: {speaker_info['total_words']:,}",
                f"  - Phrase Count: {speaker_info['phrase_count']:,}"
            ])
        
        # Add processing information
        content_lines.extend([
            f"",
            f"PROCESSING INFORMATION",
            f"----------------------",
            f"Job ID: {data['metadata'].get('job_id', 'Unknown')}",
            f"Processing Time: {data['metadata'].get('processing_time_seconds', 0):.1f}s",
            f"Diarization Enabled: {data['metadata'].get('diarization_enabled', False)}"
        ])
        
        content = "\n".join(content_lines)
        file_path = output_dir / f"{base_name}_transcript_summary.txt"
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        return str(file_path)
    
    async def _create_srt_file(
        self,
        output_dir: Path,
        base_name: str,
        data: Dict[str, Any]
    ) -> str:
        """Create SRT subtitle file."""
        # Import the processor to use its SRT generation method
        from .transcript_processor import TranscriptProcessor
        processor = TranscriptProcessor()
        
        srt_content = processor.create_srt_content(data['phrases'])
        file_path = output_dir / f"{base_name}_transcript.srt"
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(srt_content)
        
        return str(file_path)
    
    async def _create_vtt_file(
        self,
        output_dir: Path,
        base_name: str,
        data: Dict[str, Any]
    ) -> str:
        """Create WebVTT subtitle file."""
        # Import the processor to use its VTT generation method
        from .transcript_processor import TranscriptProcessor
        processor = TranscriptProcessor()
        
        vtt_content = processor.create_vtt_content(data['phrases'])
        file_path = output_dir / f"{base_name}_transcript.vtt"
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(vtt_content)
        
        return str(file_path)
    
    async def _create_speaker_analysis_file(
        self,
        output_dir: Path,
        base_name: str,
        data: Dict[str, Any]
    ) -> str:
        """Create detailed speaker analysis file."""
        content_lines = [
            f"SPEAKER ANALYSIS REPORT",
            f"======================",
            f"",
            f"Audio File: {base_name}",
            f"Total Duration: {data['duration_formatted']}",
            f"Number of Speakers: {len(data['speakers'])}",
            f"",
            f"SPEAKER BREAKDOWN",
            f"-----------------"
        ]
        
        # Sort speakers by speaking time
        speakers_sorted = sorted(
            data['speakers'].items(),
            key=lambda x: x[1]['total_duration_ms'],
            reverse=True
        )
        
        for speaker_id, speaker_info in speakers_sorted:
            speaking_time_s = speaker_info['total_duration_ms'] / 1000
            first_appearance_s = speaker_info['first_appearance_ms'] / 1000
            last_appearance_s = speaker_info['last_appearance_ms'] / 1000
            
            content_lines.extend([
                f"",
                f"SPEAKER {speaker_id}",
                f"----------",
                f"Speaking Time: {speaking_time_s:.1f} seconds ({speaker_info['speaking_percentage']:.1f}%)",
                f"Word Count: {speaker_info['total_words']:,} words",
                f"Phrase Count: {speaker_info['phrase_count']:,} phrases",
                f"Average Words per Phrase: {speaker_info['total_words'] / max(1, speaker_info['phrase_count']):.1f}",
                f"First Appearance: {first_appearance_s:.1f}s",
                f"Last Appearance: {last_appearance_s:.1f}s",
                f"Active Duration: {(last_appearance_s - first_appearance_s):.1f}s"
            ])
        
        # Add conversation dynamics
        content_lines.extend([
            f"",
            f"CONVERSATION DYNAMICS",
            f"--------------------"
        ])
        
        # Calculate speaker transitions
        transitions = 0
        last_speaker = None
        for phrase in data['phrases']:
            current_speaker = phrase.get('speaker', 1)
            if last_speaker is not None and current_speaker != last_speaker:
                transitions += 1
            last_speaker = current_speaker
        
        content_lines.extend([
            f"Speaker Transitions: {transitions}",
            f"Average Time per Speaker Turn: {data['duration_ms'] / 1000 / max(1, transitions):.1f}s"
        ])
        
        content = "\n".join(content_lines)
        file_path = output_dir / f"{base_name}_speaker_analysis.txt"
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        return str(file_path)