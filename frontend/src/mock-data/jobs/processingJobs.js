/**
 * Processing Jobs Mock Data
 * Jobs currently in progress with realistic progress states
 */

// Helper function to generate recent timestamps
const generateRecentTimestamp = (minutesAgo) => {
  const date = new Date();
  date.setMinutes(date.getMinutes() - minutesAgo);
  return date.toISOString();
};

export const processingJobs = [
  {
    id: 'proc-001',
    userId: 'user-alice',
    service: 'document-intelligence',
    fileName: 'annual-compliance-report-2024.pdf',
    fileSize: 15728640, // 15 MB
    pageCount: 58,
    estimatedProcessingTime: 45000, // 45 seconds estimated
    elapsedTime: 28000, // 28 seconds elapsed
    estimatedCost: 0.58,
    timestamp: generateRecentTimestamp(28),
    status: 'processing',
    progress: {
      percentage: 62,
      currentStage: 'extracting_tables',
      stages: [
        { name: 'upload', status: 'completed', duration: 2000 },
        { name: 'validation', status: 'completed', duration: 1500 },
        { name: 'text_extraction', status: 'completed', duration: 12000 },
        { name: 'extracting_tables', status: 'processing', estimatedDuration: 15000 },
        { name: 'layout_analysis', status: 'pending', estimatedDuration: 8000 },
        { name: 'finalizing', status: 'pending', estimatedDuration: 3000 }
      ],
      pagesProcessed: 36,
      tablesFound: 8,
      currentPage: 37
    },
    metadata: {
      mimeType: 'application/pdf',
      analysisType: 'comprehensive',
      language: 'en-US'
    }
  },
  {
    id: 'proc-002',
    userId: 'user-bob',
    service: 'translation',
    fileName: 'user-manual-chinese-v2.docx',
    fileSize: 4567890, // 4.35 MB
    characterCount: 234000,
    estimatedProcessingTime: 18000,
    elapsedTime: 7200,
    estimatedCost: 2.34,
    timestamp: generateRecentTimestamp(7),
    status: 'processing',
    progress: {
      percentage: 40,
      currentStage: 'translating',
      stages: [
        { name: 'upload', status: 'completed', duration: 1000 },
        { name: 'validation', status: 'completed', duration: 800 },
        { name: 'language_detection', status: 'completed', duration: 2000 },
        { name: 'translating', status: 'processing', estimatedDuration: 12000 },
        { name: 'formatting', status: 'pending', estimatedDuration: 2000 },
        { name: 'finalizing', status: 'pending', estimatedDuration: 1200 }
      ],
      charactersTranslated: 93600,
      sourceLanguage: 'zh-CN',
      targetLanguage: 'en',
      qualityScore: 0.94
    },
    metadata: {
      mimeType: 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
      translationType: 'document',
      preserveFormatting: true
    }
  },
  {
    id: 'proc-003',
    userId: 'user-charlie',
    service: 'transcription',
    fileName: 'quarterly-earnings-call-q1-2024.wav',
    fileSize: 178956800, // 170.6 MB
    audioDuration: 7200, // 2 hours
    estimatedProcessingTime: 300000, // 5 minutes (batch)
    elapsedTime: 180000, // 3 minutes elapsed
    estimatedCost: 1.44, // 2 hours * $0.18 batch rate + $0.36 * 2 = 1.44
    timestamp: generateRecentTimestamp(180),
    status: 'processing',
    progress: {
      percentage: 60,
      currentStage: 'transcribing',
      stages: [
        { name: 'upload', status: 'completed', duration: 5000 },
        { name: 'validation', status: 'completed', duration: 2000 },
        { name: 'audio_analysis', status: 'completed', duration: 15000 },
        { name: 'transcribing', status: 'processing', estimatedDuration: 240000 },
        { name: 'speaker_diarization', status: 'pending', estimatedDuration: 30000 },
        { name: 'finalizing', status: 'pending', estimatedDuration: 8000 }
      ],
      secondsTranscribed: 4320, // 72 minutes
      speakersDetected: 4,
      wordsTranscribed: 9840,
      confidenceScore: 0.87
    },
    metadata: {
      mimeType: 'audio/wav',
      transcriptionType: 'batch',
      sampleRate: 48000,
      channels: 2
    }
  },
  {
    id: 'proc-004',
    userId: 'user-diana',
    service: 'document-intelligence',
    fileName: 'medical-records-batch-2024.pdf',
    fileSize: 8923456, // 8.51 MB
    pageCount: 34,
    estimatedProcessingTime: 28000,
    elapsedTime: 12000,
    estimatedCost: 0.34,
    timestamp: generateRecentTimestamp(12),
    status: 'processing',
    progress: {
      percentage: 43,
      currentStage: 'text_extraction',
      stages: [
        { name: 'upload', status: 'completed', duration: 2500 },
        { name: 'validation', status: 'completed', duration: 1800 },
        { name: 'text_extraction', status: 'processing', estimatedDuration: 18000 },
        { name: 'layout_analysis', status: 'pending', estimatedDuration: 5000 },
        { name: 'finalizing', status: 'pending', estimatedDuration: 2000 }
      ],
      pagesProcessed: 15,
      currentPage: 16,
      tablesFound: 2
    },
    metadata: {
      mimeType: 'application/pdf',
      analysisType: 'layout',
      language: 'en-US'
    }
  },
  {
    id: 'proc-005',
    userId: 'user-eve',
    service: 'translation',
    fileName: 'corporate-policies-spanish.txt',
    fileSize: 567890, // 554 KB
    characterCount: 87000,
    estimatedProcessingTime: 6500,
    elapsedTime: 1800,
    estimatedCost: 0.87,
    timestamp: generateRecentTimestamp(2),
    status: 'processing',
    progress: {
      percentage: 28,
      currentStage: 'language_detection',
      stages: [
        { name: 'upload', status: 'completed', duration: 600 },
        { name: 'validation', status: 'completed', duration: 400 },
        { name: 'language_detection', status: 'processing', estimatedDuration: 1500 },
        { name: 'translating', status: 'pending', estimatedDuration: 3500 },
        { name: 'finalizing', status: 'pending', estimatedDuration: 500 }
      ],
      charactersTranslated: 0,
      sourceLanguage: 'es', // detected
      targetLanguage: 'en',
      qualityScore: null
    },
    metadata: {
      mimeType: 'text/plain',
      translationType: 'text',
      preserveFormatting: false
    }
  },
  {
    id: 'proc-006',
    userId: 'user-frank',
    service: 'transcription',
    fileName: 'team-standup-recording.mp3',
    fileSize: 23456789, // 22.4 MB
    audioDuration: 1800, // 30 minutes
    estimatedProcessingTime: 60000, // 1 minute (fast)
    elapsedTime: 35000, // 35 seconds elapsed
    estimatedCost: 0.18, // 0.5 hours * $0.36
    timestamp: generateRecentTimestamp(35),
    status: 'processing',
    progress: {
      percentage: 58,
      currentStage: 'transcribing',
      stages: [
        { name: 'upload', status: 'completed', duration: 3000 },
        { name: 'validation', status: 'completed', duration: 1500 },
        { name: 'audio_analysis', status: 'completed', duration: 8000 },
        { name: 'transcribing', status: 'processing', estimatedDuration: 45000 },
        { name: 'finalizing', status: 'pending', estimatedDuration: 2500 }
      ],
      secondsTranscribed: 1044, // ~17 minutes
      speakersDetected: 6,
      wordsTranscribed: 2890,
      confidenceScore: 0.91
    },
    metadata: {
      mimeType: 'audio/mpeg',
      transcriptionType: 'fast',
      sampleRate: 44100,
      channels: 2
    }
  }
];

export default processingJobs;