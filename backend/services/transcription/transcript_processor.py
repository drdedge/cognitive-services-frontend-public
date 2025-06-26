#backend/services/transcription/transcript_processor.py
"""
Transcript processor with chunking and speaker analysis
======================================================

Processes raw Azure Speech Services transcription results into user-friendly formats,
implementing intelligent chunking, speaker analysis, and multiple output formats:

## Key Features:
----------------
- 1-minute time-based chunking with sentence preservation
- Speaker diarization analysis and statistics
- Multiple timestamp formats (mm:ss, SRT, VTT)
- Confidence score tracking per phrase
- Words per minute calculation
- Speaker transition analysis
- SRT and WebVTT subtitle generation

## Processing Pipeline:
----------------------
- Extract phrases and timing from Azure response
- Group phrases into 1-minute chunks
- Identify and analyze unique speakers
- Format timestamps for different outputs
- Calculate comprehensive statistics

"""

import re
from typing import List, Dict, Any, Tuple, Optional
from datetime import timedelta

from utils.logging import get_logger

logger = get_logger(__name__)


class TranscriptProcessor:
    """Processes raw transcription results into formatted output."""
    
    def __init__(self):
        """Initialize the processor."""
        self.chunk_duration_ms = 60000  # 1 minute in milliseconds
    
    def process_transcription_result(
        self,
        azure_result: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Process Azure transcription result into structured format.
        
        Args:
            azure_result: Raw result from Azure Speech API
            
        Returns:
            Processed transcription data
        """
        try:
            # Extract basic info
            duration_ms = azure_result.get('durationMilliseconds', 0)
            combined_text = ""
            
            # Extract combined phrases (full transcript)
            combined_phrases = azure_result.get('combinedPhrases', [])
            if combined_phrases:
                combined_text = combined_phrases[0].get('text', '')
            
            # Process individual phrases
            phrases = azure_result.get('phrases', [])
            
            # Calculate statistics
            stats = self._calculate_statistics(phrases, duration_ms)
            
            # Create time-chunked transcript
            chunked_transcript = self._create_time_chunks(phrases, self.chunk_duration_ms)
            
            # Identify speakers
            speakers = self._identify_speakers(phrases)
            
            return {
                'duration_ms': duration_ms,
                'duration_formatted': self._format_duration(duration_ms),
                'combined_text': combined_text,
                'phrases': phrases,
                'chunked_transcript': chunked_transcript,
                'speakers': speakers,
                'statistics': stats,
                'metadata': azure_result.get('metadata', {})
            }
            
        except Exception as e:
            logger.error(f"Error processing transcription result: {e}")
            raise
    
    def _create_time_chunks(
        self,
        phrases: List[Dict[str, Any]],
        chunk_duration_ms: int
    ) -> List[Dict[str, Any]]:
        """
        Split transcript into time-based chunks while preserving sentences.
        
        Args:
            phrases: List of phrase objects from Azure
            chunk_duration_ms: Target chunk duration in milliseconds
            
        Returns:
            List of transcript chunks
        """
        chunks = []
        current_chunk = {
            'start_ms': 0,
            'end_ms': 0,
            'segments': [],
            'text': '',
            'speakers': set()
        }
        
        chunk_start_ms = 0
        
        for phrase in phrases:
            phrase_start = phrase.get('offsetMilliseconds', 0)
            phrase_duration = phrase.get('durationMilliseconds', 0)
            phrase_end = phrase_start + phrase_duration
            speaker = phrase.get('speaker', 1)
            
            # Check if we should start a new chunk
            if phrase_start >= chunk_start_ms + chunk_duration_ms and current_chunk['segments']:
                # Finalize current chunk
                current_chunk['end_ms'] = current_chunk['segments'][-1]['end_ms']
                current_chunk['speakers'] = sorted(list(current_chunk['speakers']))
                current_chunk['text'] = self._combine_segment_text(current_chunk['segments'])
                chunks.append(current_chunk)
                
                # Start new chunk
                chunk_start_ms = phrase_start
                current_chunk = {
                    'start_ms': phrase_start,
                    'end_ms': phrase_end,
                    'segments': [],
                    'text': '',
                    'speakers': set()
                }
            
            # Add phrase to current chunk
            segment = {
                'start_ms': phrase_start,
                'end_ms': phrase_end,
                'speaker': speaker,
                'text': phrase.get('text', ''),
                'confidence': phrase.get('confidence', 0.0)
            }
            
            current_chunk['segments'].append(segment)
            current_chunk['speakers'].add(speaker)
            current_chunk['end_ms'] = max(current_chunk['end_ms'], phrase_end)
        
        # Add final chunk if it has content
        if current_chunk['segments']:
            current_chunk['speakers'] = sorted(list(current_chunk['speakers']))
            current_chunk['text'] = self._combine_segment_text(current_chunk['segments'])
            chunks.append(current_chunk)
        
        # Format chunks for output
        formatted_chunks = []
        for i, chunk in enumerate(chunks):
            formatted_chunks.append({
                'chunk_number': i + 1,
                'start_time': self._ms_to_time_string(chunk['start_ms']),
                'end_time': self._ms_to_time_string(chunk['end_ms']),
                'duration_ms': chunk['end_ms'] - chunk['start_ms'],
                'speakers': chunk['speakers'],
                'segments': chunk['segments'],
                'formatted_text': self._format_chunk_text(chunk)
            })
        
        return formatted_chunks
    
    def _format_chunk_text(self, chunk: Dict[str, Any]) -> str:
        """
        Format chunk text with timestamps and speakers.
        
        Args:
            chunk: Chunk data
            
        Returns:
            Formatted text with [mm:ss-mm:ss][Speaker X] format
        """
        start_time = self._ms_to_time_string(chunk['start_ms'])
        end_time = self._ms_to_time_string(chunk['end_ms'])
        
        # Group consecutive segments by speaker
        formatted_lines = []
        current_speaker = None
        current_text = []
        
        for segment in chunk['segments']:
            speaker = segment['speaker']
            text = segment['text'].strip()
            
            if speaker != current_speaker:
                # Output previous speaker's text
                if current_speaker is not None and current_text:
                    speaker_text = ' '.join(current_text)
                    formatted_lines.append(f"[Speaker {current_speaker}] {speaker_text}")
                
                current_speaker = speaker
                current_text = [text]
            else:
                current_text.append(text)
        
        # Output final speaker's text
        if current_speaker is not None and current_text:
            speaker_text = ' '.join(current_text)
            formatted_lines.append(f"[Speaker {current_speaker}] {speaker_text}")
        
        # Combine with timestamp
        chunk_header = f"[{start_time}-{end_time}]"
        if len(formatted_lines) == 1:
            return f"{chunk_header}{formatted_lines[0]}"
        else:
            return f"{chunk_header}\n" + '\n'.join(formatted_lines)
    
    def _combine_segment_text(self, segments: List[Dict[str, Any]]) -> str:
        """Combine segment texts into a single string."""
        texts = [seg['text'].strip() for seg in segments if seg.get('text')]
        return ' '.join(texts)
    
    def _identify_speakers(self, phrases: List[Dict[str, Any]]) -> Dict[int, Dict[str, Any]]:
        """
        Identify unique speakers and calculate their statistics.
        
        Args:
            phrases: List of phrases from transcription
            
        Returns:
            Dictionary of speaker information
        """
        speakers = {}
        
        for phrase in phrases:
            speaker_id = phrase.get('speaker', 1)
            
            if speaker_id not in speakers:
                speakers[speaker_id] = {
                    'id': speaker_id,
                    'phrase_count': 0,
                    'total_duration_ms': 0,
                    'total_words': 0,
                    'first_appearance_ms': phrase.get('offsetMilliseconds', 0),
                    'last_appearance_ms': phrase.get('offsetMilliseconds', 0)
                }
            
            speaker = speakers[speaker_id]
            speaker['phrase_count'] += 1
            speaker['total_duration_ms'] += phrase.get('durationMilliseconds', 0)
            
            # Count words
            text = phrase.get('text', '')
            speaker['total_words'] += len(text.split())
            
            # Update last appearance
            phrase_end = phrase.get('offsetMilliseconds', 0) + phrase.get('durationMilliseconds', 0)
            speaker['last_appearance_ms'] = max(speaker['last_appearance_ms'], phrase_end)
        
        # Calculate speaking percentage for each speaker
        total_duration = sum(s['total_duration_ms'] for s in speakers.values())
        for speaker in speakers.values():
            speaker['speaking_percentage'] = (
                (speaker['total_duration_ms'] / total_duration * 100) if total_duration > 0 else 0
            )
        
        return speakers
    
    def _calculate_statistics(
        self,
        phrases: List[Dict[str, Any]],
        total_duration_ms: int
    ) -> Dict[str, Any]:
        """Calculate transcription statistics."""
        total_words = 0
        total_confidence = 0.0
        confidence_count = 0
        
        for phrase in phrases:
            text = phrase.get('text', '')
            total_words += len(text.split())
            
            confidence = phrase.get('confidence')
            if confidence is not None:
                total_confidence += confidence
                confidence_count += 1
        
        avg_confidence = (total_confidence / confidence_count) if confidence_count > 0 else 0.0
        
        # Calculate words per minute
        duration_minutes = total_duration_ms / 60000
        wpm = (total_words / duration_minutes) if duration_minutes > 0 else 0
        
        return {
            'total_words': total_words,
            'total_phrases': len(phrases),
            'average_confidence': round(avg_confidence, 4),
            'words_per_minute': round(wpm, 1),
            'duration_seconds': total_duration_ms / 1000,
            'duration_formatted': self._format_duration(total_duration_ms)
        }
    
    def _ms_to_time_string(self, milliseconds: int) -> str:
        """
        Convert milliseconds to mm:ss format.
        
        Args:
            milliseconds: Time in milliseconds
            
        Returns:
            Formatted time string (mm:ss)
        """
        total_seconds = milliseconds / 1000
        minutes = int(total_seconds // 60)
        seconds = int(total_seconds % 60)
        return f"{minutes:02d}:{seconds:02d}"
    
    def _format_duration(self, milliseconds: int) -> str:
        """
        Format duration in human-readable format.
        
        Args:
            milliseconds: Duration in milliseconds
            
        Returns:
            Formatted duration string
        """
        total_seconds = milliseconds / 1000
        hours = int(total_seconds // 3600)
        minutes = int((total_seconds % 3600) // 60)
        seconds = int(total_seconds % 60)
        
        if hours > 0:
            return f"{hours}h {minutes}m {seconds}s"
        elif minutes > 0:
            return f"{minutes}m {seconds}s"
        else:
            return f"{seconds}s"
    
    def create_srt_content(self, phrases: List[Dict[str, Any]]) -> str:
        """Create SRT subtitle content from phrases."""
        srt_lines = []
        
        for i, phrase in enumerate(phrases, 1):
            start_ms = phrase.get('offsetMilliseconds', 0)
            duration_ms = phrase.get('durationMilliseconds', 0)
            end_ms = start_ms + duration_ms
            
            start_time = self._ms_to_srt_time(start_ms)
            end_time = self._ms_to_srt_time(end_ms)
            text = phrase.get('text', '')
            speaker = phrase.get('speaker', 1)
            
            # Add speaker label if diarization is enabled
            if speaker != 1 or len(set(p.get('speaker', 1) for p in phrases)) > 1:
                text = f"[Speaker {speaker}] {text}"
            
            srt_lines.append(str(i))
            srt_lines.append(f"{start_time} --> {end_time}")
            srt_lines.append(text)
            srt_lines.append("")
        
        return "\n".join(srt_lines)
    
    def create_vtt_content(self, phrases: List[Dict[str, Any]]) -> str:
        """Create WebVTT subtitle content from phrases."""
        vtt_lines = ["WEBVTT", ""]
        
        for phrase in phrases:
            start_ms = phrase.get('offsetMilliseconds', 0)
            duration_ms = phrase.get('durationMilliseconds', 0)
            end_ms = start_ms + duration_ms
            
            start_time = self._ms_to_vtt_time(start_ms)
            end_time = self._ms_to_vtt_time(end_ms)
            text = phrase.get('text', '')
            speaker = phrase.get('speaker', 1)
            
            # Add speaker label if diarization is enabled
            if speaker != 1 or len(set(p.get('speaker', 1) for p in phrases)) > 1:
                text = f"[Speaker {speaker}] {text}"
            
            vtt_lines.append(f"{start_time} --> {end_time}")
            vtt_lines.append(text)
            vtt_lines.append("")
        
        return "\n".join(vtt_lines)
    
    def _ms_to_srt_time(self, milliseconds: int) -> str:
        """Convert milliseconds to SRT time format (HH:MM:SS,mmm)."""
        td = timedelta(milliseconds=milliseconds)
        hours = int(td.total_seconds() // 3600)
        minutes = int((td.total_seconds() % 3600) // 60)
        seconds = int(td.total_seconds() % 60)
        millis = int(milliseconds % 1000)
        return f"{hours:02d}:{minutes:02d}:{seconds:02d},{millis:03d}"
    
    def _ms_to_vtt_time(self, milliseconds: int) -> str:
        """Convert milliseconds to WebVTT time format (HH:MM:SS.mmm)."""
        td = timedelta(milliseconds=milliseconds)
        hours = int(td.total_seconds() // 3600)
        minutes = int((td.total_seconds() % 3600) // 60)
        seconds = int(td.total_seconds() % 60)
        millis = int(milliseconds % 1000)
        return f"{hours:02d}:{minutes:02d}:{seconds:02d}.{millis:03d}"