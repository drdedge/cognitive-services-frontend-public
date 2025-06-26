/**
 * Completed Jobs Mock Data
 * Comprehensive set of successfully completed jobs with realistic results
 */

// Helper function to generate timestamps in the last 30 days
const generateTimestamp = (daysAgo) => {
  const date = new Date();
  date.setDate(date.getDate() - daysAgo);
  date.setHours(Math.floor(Math.random() * 24), Math.floor(Math.random() * 60));
  return date.toISOString();
};

export const completedJobs = [
  // Document Intelligence Jobs
  {
    id: 'doc-001',
    userId: 'user-alice',
    service: 'document-intelligence',
    fileName: 'quarterly-financial-report-q4-2024.pdf',
    fileSize: 3247680, // 3.1 MB
    pageCount: 24,
    processingTime: 18000, // 18 seconds
    cost: 0.24, // $10 per 1000 pages = $0.01 per page
    timestamp: generateTimestamp(1),
    status: 'completed',
    results: {
      tablesExtracted: 8,
      confidenceScore: 0.94,
      textLength: 15420,
      extractedTables: [
        { name: 'Revenue_Summary.csv', size: 2048 },
        { name: 'Quarterly_Comparison.csv', size: 1536 },
        { name: 'Department_Breakdown.xlsx', size: 4096 }
      ],
      extractedText: 'Financial_Report_Q4_2024.md'
    },
    metadata: {
      mimeType: 'application/pdf',
      analysisType: 'comprehensive',
      language: 'en-US'
    }
  },
  {
    id: 'doc-002',
    userId: 'user-bob',
    service: 'document-intelligence',
    fileName: 'contract-template-2024.docx',
    fileSize: 856320, // 836 KB
    pageCount: 8,
    processingTime: 6500,
    cost: 0.08,
    timestamp: generateTimestamp(2),
    status: 'completed',
    results: {
      tablesExtracted: 2,
      confidenceScore: 0.98,
      textLength: 4280,
      extractedTables: [
        { name: 'Terms_And_Conditions.csv', size: 1024 }
      ],
      extractedText: 'Contract_Template_2024.md'
    },
    metadata: {
      mimeType: 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
      analysisType: 'layout',
      language: 'en-US'
    }
  },
  {
    id: 'doc-003',
    userId: 'user-charlie',
    service: 'document-intelligence',
    fileName: 'invoice-batch-march-2024.pdf',
    fileSize: 12458496, // 11.9 MB
    pageCount: 45,
    processingTime: 32000,
    cost: 0.45,
    timestamp: generateTimestamp(3),
    status: 'completed',
    results: {
      tablesExtracted: 15,
      confidenceScore: 0.91,
      textLength: 8940,
      extractedTables: [
        { name: 'Invoice_Details.xlsx', size: 8192 },
        { name: 'Payment_Terms.csv', size: 2048 }
      ],
      extractedText: 'Invoice_Batch_March_2024.md'
    },
    metadata: {
      mimeType: 'application/pdf',
      analysisType: 'comprehensive',
      language: 'en-US'
    }
  },

  // Translation Jobs
  {
    id: 'trans-001',
    userId: 'user-diana',
    service: 'translation',
    fileName: 'product-manual-spanish.docx',
    fileSize: 2145280, // 2.04 MB
    characterCount: 125000,
    processingTime: 8500,
    cost: 1.25, // $10 per million characters
    timestamp: generateTimestamp(1),
    status: 'completed',
    results: {
      sourceLanguage: 'es',
      targetLanguage: 'en',
      autoDetected: false,
      confidenceScore: 0.96,
      translatedFile: 'product-manual-english.docx',
      wordCount: 18750,
      translationQuality: 'high'
    },
    metadata: {
      mimeType: 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
      translationType: 'document',
      preserveFormatting: true
    }
  },
  {
    id: 'trans-002',
    userId: 'user-eve',
    service: 'translation',
    fileName: 'legal-terms-french.pdf',
    fileSize: 1843200, // 1.76 MB
    characterCount: 89000,
    processingTime: 6200,
    cost: 0.89,
    timestamp: generateTimestamp(2),
    status: 'completed',
    results: {
      sourceLanguage: 'fr',
      targetLanguage: 'en',
      autoDetected: true,
      confidenceScore: 0.93,
      translatedFile: 'legal-terms-english.pdf',
      wordCount: 13350,
      translationQuality: 'high'
    },
    metadata: {
      mimeType: 'application/pdf',
      translationType: 'document',
      preserveFormatting: true
    }
  },
  {
    id: 'trans-003',
    userId: 'user-alice',
    service: 'translation',
    fileName: 'marketing-content-german.txt',
    fileSize: 245760, // 240 KB
    characterCount: 45000,
    processingTime: 3100,
    cost: 0.45,
    timestamp: generateTimestamp(4),
    status: 'completed',
    results: {
      sourceLanguage: 'de',
      targetLanguage: 'en',
      autoDetected: false,
      confidenceScore: 0.97,
      translatedFile: 'marketing-content-english.txt',
      wordCount: 6750,
      translationQuality: 'high'
    },
    metadata: {
      mimeType: 'text/plain',
      translationType: 'text',
      preserveFormatting: false
    }
  },

  // Transcription Jobs
  {
    id: 'audio-001',
    userId: 'user-frank',
    service: 'transcription',
    fileName: 'board-meeting-q1-2024.mp3',
    fileSize: 45678592, // 43.5 MB
    audioDuration: 3600, // 1 hour
    processingTime: 120000, // 2 minutes
    cost: 0.36, // Fast transcription rate
    timestamp: generateTimestamp(1),
    status: 'completed',
    results: {
      transcriptionType: 'fast',
      speakers: 5,
      wordCount: 8500,
      confidenceScore: 0.88,
      transcriptFormats: [
        { format: 'txt', file: 'board-meeting-q1-2024.txt' },
        { format: 'srt', file: 'board-meeting-q1-2024.srt' },
        { format: 'vtt', file: 'board-meeting-q1-2024.vtt' },
        { format: 'json', file: 'board-meeting-q1-2024.json' }
      ],
      speakerDiarization: true,
      timestamps: true
    },
    metadata: {
      mimeType: 'audio/mpeg',
      sampleRate: 44100,
      channels: 2,
      bitrate: 128
    }
  },
  {
    id: 'audio-002',
    userId: 'user-grace',
    service: 'transcription',
    fileName: 'customer-interview-session-1.wav',
    fileSize: 89654272, // 85.5 MB
    audioDuration: 2700, // 45 minutes
    processingTime: 90000, // 1.5 minutes
    cost: 0.27, // Fast transcription rate
    timestamp: generateTimestamp(2),
    status: 'completed',
    results: {
      transcriptionType: 'fast',
      speakers: 2,
      wordCount: 6750,
      confidenceScore: 0.92,
      transcriptFormats: [
        { format: 'txt', file: 'customer-interview-session-1.txt' },
        { format: 'srt', file: 'customer-interview-session-1.srt' },
        { format: 'json', file: 'customer-interview-session-1.json' }
      ],
      speakerDiarization: true,
      timestamps: true
    },
    metadata: {
      mimeType: 'audio/wav',
      sampleRate: 48000,
      channels: 1,
      bitrate: 256
    }
  },
  {
    id: 'audio-003',
    userId: 'user-henry',
    service: 'transcription',
    fileName: 'training-webinar-march-2024.m4a',
    fileSize: 125829120, // 120 MB
    audioDuration: 5400, // 1.5 hours
    processingTime: 180000, // 3 minutes (batch processing)
    cost: 0.27, // Batch transcription rate (1.5 * 0.18)
    timestamp: generateTimestamp(5),
    status: 'completed',
    results: {
      transcriptionType: 'batch',
      speakers: 3,
      wordCount: 12750,
      confidenceScore: 0.95,
      transcriptFormats: [
        { format: 'txt', file: 'training-webinar-march-2024.txt' },
        { format: 'srt', file: 'training-webinar-march-2024.srt' },
        { format: 'vtt', file: 'training-webinar-march-2024.vtt' },
        { format: 'json', file: 'training-webinar-march-2024.json' }
      ],
      speakerDiarization: true,
      timestamps: true
    },
    metadata: {
      mimeType: 'audio/mp4',
      sampleRate: 44100,
      channels: 2,
      bitrate: 192
    }
  },

  // Additional jobs for statistical diversity
  {
    id: 'doc-004',
    userId: 'user-iris',
    service: 'document-intelligence',
    fileName: 'research-paper-ai-2024.pdf',
    fileSize: 5432768, // 5.18 MB
    pageCount: 32,
    processingTime: 24000,
    cost: 0.32,
    timestamp: generateTimestamp(6),
    status: 'completed',
    results: {
      tablesExtracted: 12,
      confidenceScore: 0.89,
      textLength: 28400,
      extractedTables: [
        { name: 'Research_Data.xlsx', size: 6144 },
        { name: 'Statistical_Analysis.csv', size: 3072 }
      ],
      extractedText: 'Research_Paper_AI_2024.md'
    },
    metadata: {
      mimeType: 'application/pdf',
      analysisType: 'comprehensive',
      language: 'en-US'
    }
  },
  {
    id: 'trans-004',
    userId: 'user-jack',
    service: 'translation',
    fileName: 'technical-specifications-japanese.docx',
    fileSize: 3456789, // 3.3 MB
    characterCount: 156000,
    processingTime: 11000,
    cost: 1.56,
    timestamp: generateTimestamp(7),
    status: 'completed',
    results: {
      sourceLanguage: 'ja',
      targetLanguage: 'en',
      autoDetected: false,
      confidenceScore: 0.91,
      translatedFile: 'technical-specifications-english.docx',
      wordCount: 23400,
      translationQuality: 'medium'
    },
    metadata: {
      mimeType: 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
      translationType: 'document',
      preserveFormatting: true
    }
  },
  {
    id: 'audio-004',
    userId: 'user-karen',
    service: 'transcription',
    fileName: 'podcast-episode-12.mp3',
    fileSize: 67108864, // 64 MB
    audioDuration: 4200, // 70 minutes
    processingTime: 210000, // 3.5 minutes (batch)
    cost: 0.21, // Batch rate
    timestamp: generateTimestamp(8),
    status: 'completed',
    results: {
      transcriptionType: 'batch',
      speakers: 2,
      wordCount: 9800,
      confidenceScore: 0.93,
      transcriptFormats: [
        { format: 'txt', file: 'podcast-episode-12.txt' },
        { format: 'srt', file: 'podcast-episode-12.srt' },
        { format: 'json', file: 'podcast-episode-12.json' }
      ],
      speakerDiarization: true,
      timestamps: true
    },
    metadata: {
      mimeType: 'audio/mpeg',
      sampleRate: 44100,
      channels: 2,
      bitrate: 128
    }
  }
];

export default completedJobs;