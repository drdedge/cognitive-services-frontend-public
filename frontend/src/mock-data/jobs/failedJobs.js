/**
 * Failed Jobs Mock Data
 * Jobs that failed with various error conditions and reasons
 */

// Helper function to generate timestamps in the last 7 days
const generateFailedTimestamp = (daysAgo) => {
  const date = new Date();
  date.setDate(date.getDate() - daysAgo);
  date.setHours(Math.floor(Math.random() * 24), Math.floor(Math.random() * 60));
  return date.toISOString();
};

export const failedJobs = [
  {
    id: 'fail-001',
    userId: 'user-alice',
    service: 'document-intelligence',
    fileName: 'corrupted-scan.pdf',
    fileSize: 234567,
    pageCount: null, // Could not determine
    processingTime: 5000, // Failed after 5 seconds
    cost: 0.00, // No cost for failed jobs
    timestamp: generateFailedTimestamp(1),
    status: 'failed',
    error: {
      code: 'CORRUPTED_FILE',
      message: 'The uploaded file appears to be corrupted and cannot be processed',
      details: 'PDF header is malformed. File may have been corrupted during upload or is not a valid PDF.',
      category: 'file_error',
      retryable: false,
      suggestions: [
        'Verify the file is not corrupted',
        'Try re-uploading the file',
        'Convert to a different format if possible'
      ]
    },
    progress: {
      percentage: 15,
      currentStage: 'validation',
      failedAt: 'file_integrity_check',
      stages: [
        { name: 'upload', status: 'completed', duration: 1200 },
        { name: 'validation', status: 'failed', duration: 3800 }
      ]
    },
    metadata: {
      mimeType: 'application/pdf',
      analysisType: 'comprehensive',
      attemptCount: 1
    }
  },
  {
    id: 'fail-002',
    userId: 'user-bob',
    service: 'translation',
    fileName: 'empty-document.docx',
    fileSize: 12345,
    characterCount: 0,
    processingTime: 3200,
    cost: 0.00,
    timestamp: generateFailedTimestamp(2),
    status: 'failed',
    error: {
      code: 'EMPTY_DOCUMENT',
      message: 'Document contains no translatable text',
      details: 'The uploaded document appears to be empty or contains only formatting without any text content.',
      category: 'content_error',
      retryable: false,
      suggestions: [
        'Verify the document contains text',
        'Check if the document is in a supported format',
        'Ensure the document is not password protected'
      ]
    },
    progress: {
      percentage: 25,
      currentStage: 'language_detection',
      failedAt: 'content_analysis',
      stages: [
        { name: 'upload', status: 'completed', duration: 800 },
        { name: 'validation', status: 'completed', duration: 600 },
        { name: 'language_detection', status: 'failed', duration: 1800 }
      ]
    },
    metadata: {
      mimeType: 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
      translationType: 'document',
      attemptCount: 1
    }
  },
  {
    id: 'fail-003',
    userId: 'user-charlie',
    service: 'transcription',
    fileName: 'low-quality-audio.wav',
    fileSize: 45678901, // 43.5 MB
    audioDuration: 3600, // 1 hour
    processingTime: 45000, // Failed after 45 seconds
    cost: 0.00,
    timestamp: generateFailedTimestamp(3),
    status: 'failed',
    error: {
      code: 'POOR_AUDIO_QUALITY',
      message: 'Audio quality is too poor for reliable transcription',
      details: 'The audio file has very low signal-to-noise ratio, making speech recognition unreliable. Confidence scores below acceptable threshold.',
      category: 'quality_error',
      retryable: true,
      suggestions: [
        'Improve audio quality by reducing background noise',
        'Use a higher quality microphone',
        'Record in a quieter environment',
        'Try noise reduction software before uploading'
      ]
    },
    progress: {
      percentage: 35,
      currentStage: 'transcribing',
      failedAt: 'quality_assessment',
      stages: [
        { name: 'upload', status: 'completed', duration: 4000 },
        { name: 'validation', status: 'completed', duration: 2000 },
        { name: 'audio_analysis', status: 'completed', duration: 12000 },
        { name: 'transcribing', status: 'failed', duration: 27000 }
      ],
      audioQualityScore: 0.23, // Very poor
      backgroundNoiseLevel: 0.85 // Very high
    },
    metadata: {
      mimeType: 'audio/wav',
      transcriptionType: 'fast',
      sampleRate: 22050, // Low sample rate
      channels: 1,
      attemptCount: 2
    }
  },
  {
    id: 'fail-004',
    userId: 'user-diana',
    service: 'document-intelligence',
    fileName: 'oversized-blueprint.pdf',
    fileSize: 157286400, // 150 MB
    pageCount: 1, // Single very large page
    processingTime: 2000,
    cost: 0.00,
    timestamp: generateFailedTimestamp(4),
    status: 'failed',
    error: {
      code: 'FILE_TOO_LARGE',
      message: 'File size exceeds maximum limit for processing',
      details: 'The uploaded file is 150MB, which exceeds the maximum file size limit of 50MB for document intelligence processing.',
      category: 'size_error',
      retryable: false,
      suggestions: [
        'Reduce file size by compressing images',
        'Split large documents into smaller files',
        'Use a lower resolution for scanned documents',
        'Convert to a more efficient format'
      ]
    },
    progress: {
      percentage: 5,
      currentStage: 'validation',
      failedAt: 'size_check',
      stages: [
        { name: 'upload', status: 'completed', duration: 1500 },
        { name: 'validation', status: 'failed', duration: 500 }
      ]
    },
    metadata: {
      mimeType: 'application/pdf',
      analysisType: 'layout',
      attemptCount: 1,
      maxSizeLimit: 52428800 // 50MB
    }
  },
  {
    id: 'fail-005',
    userId: 'user-eve',
    service: 'translation',
    fileName: 'mixed-languages.txt',
    fileSize: 345678,
    characterCount: 67000,
    processingTime: 8500,
    cost: 0.00,
    timestamp: generateFailedTimestamp(5),
    status: 'failed',
    error: {
      code: 'UNSUPPORTED_LANGUAGE',
      message: 'Document contains unsupported language or mixed languages',
      details: 'The document appears to contain text in multiple languages including some that are not supported by the translation service.',
      category: 'language_error',
      retryable: true,
      suggestions: [
        'Separate content by language',
        'Specify the source language manually',
        'Remove unsupported language content',
        'Check if all languages are supported'
      ]
    },
    progress: {
      percentage: 20,
      currentStage: 'language_detection',
      failedAt: 'language_analysis',
      stages: [
        { name: 'upload', status: 'completed', duration: 500 },
        { name: 'validation', status: 'completed', duration: 400 },
        { name: 'language_detection', status: 'failed', duration: 7600 }
      ],
      detectedLanguages: ['en', 'es', 'unknown'], // Mixed languages detected
      confidence: 0.34 // Low confidence
    },
    metadata: {
      mimeType: 'text/plain',
      translationType: 'text',
      attemptCount: 1
    }
  },
  {
    id: 'fail-006',
    userId: 'user-frank',
    service: 'transcription',
    fileName: 'instrumental-music.mp3',
    fileSize: 12345678, // 11.8 MB
    audioDuration: 900, // 15 minutes
    processingTime: 25000,
    cost: 0.00,
    timestamp: generateFailedTimestamp(6),
    status: 'failed',
    error: {
      code: 'NO_SPEECH_DETECTED',
      message: 'No speech content detected in audio file',
      details: 'The audio file appears to contain only music or instrumental audio without any human speech that can be transcribed.',
      category: 'content_error',
      retryable: false,
      suggestions: [
        'Verify the file contains speech',
        'Check audio levels and clarity',
        'Ensure speakers are audible',
        'Remove background music if possible'
      ]
    },
    progress: {
      percentage: 30,
      currentStage: 'transcribing',
      failedAt: 'speech_detection',
      stages: [
        { name: 'upload', status: 'completed', duration: 2000 },
        { name: 'validation', status: 'completed', duration: 1500 },
        { name: 'audio_analysis', status: 'completed', duration: 6000 },
        { name: 'transcribing', status: 'failed', duration: 15500 }
      ],
      speechDetected: false,
      musicDetected: true,
      speechConfidence: 0.05
    },
    metadata: {
      mimeType: 'audio/mpeg',
      transcriptionType: 'fast',
      sampleRate: 44100,
      channels: 2,
      attemptCount: 1
    }
  },
  {
    id: 'fail-007',
    userId: 'user-grace',
    service: 'document-intelligence',
    fileName: 'password-protected.pdf',
    fileSize: 2345678,
    pageCount: null,
    processingTime: 1500,
    cost: 0.00,
    timestamp: generateFailedTimestamp(7),
    status: 'failed',
    error: {
      code: 'PASSWORD_PROTECTED',
      message: 'Document is password protected and cannot be processed',
      details: 'The PDF document requires a password to access its content. Please remove password protection before uploading.',
      category: 'access_error',
      retryable: false,
      suggestions: [
        'Remove password protection from the PDF',
        'Provide the document in an unprotected format',
        'Export to a different format without protection',
        'Contact document owner for unprotected version'
      ]
    },
    progress: {
      percentage: 10,
      currentStage: 'validation',
      failedAt: 'access_check',
      stages: [
        { name: 'upload', status: 'completed', duration: 800 },
        { name: 'validation', status: 'failed', duration: 700 }
      ]
    },
    metadata: {
      mimeType: 'application/pdf',
      analysisType: 'layout',
      attemptCount: 1,
      isPasswordProtected: true
    }
  }
];

export default failedJobs;